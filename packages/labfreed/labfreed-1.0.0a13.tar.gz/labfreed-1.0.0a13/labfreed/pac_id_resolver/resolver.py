from functools import lru_cache
import logging
from typing import Self
from requests import get



from labfreed.pac_cat.pac_cat import PAC_CAT
from labfreed.pac_id.pac_id import PAC_ID
from labfreed.pac_id_resolver.services import ServiceGroup
from labfreed.pac_id_resolver.cit_v1 import CIT_v1
from labfreed.pac_id_resolver.cit_v2 import CIT_v2



''' Configure pdoc'''
__all__ = ["PAC_ID_Resolver"]

def load_cit(path):
    with open(path, 'r') as f:
        s = f.read()
        return cit_from_str(s)

    
def cit_from_str(s:str, origin:str='') -> CIT_v1|CIT_v2:
    try:
        cit2 = CIT_v2.from_yaml(s)
        cit_version = 'v2'
    except Exception:
        cit2 = None
    try:
        cit1 = CIT_v1.from_csv(s, origin)
        cit_version = 'v1'  # noqa: F841
    except Exception:
        cit1 = None
    
    cit = cit2 or cit1 or None
    return cit

@lru_cache
def _get_issuer_cit(issuer:str):
    '''Gets the issuer's cit.'''
    url = 'HTTPS://PAC.' + issuer + '/coupling-information-table'
    try:
        r = get(url, timeout=2)
        if r.status_code < 400:
            cit_str = r.text
        else: 
            logging.error(f"Could not get CIT form {issuer}")
            cit_str  = None
    except Exception:
        logging.error(f"Could not get CIT form {issuer}")
        cit_str  = None
    cit = cit_from_str(cit_str, origin=issuer)
    return cit
    


class PAC_ID_Resolver():
    def __init__(self, cits:list[CIT_v2|CIT_v1]=None) -> Self:
        '''Initialize the resolver with coupling information tables'''
        if not cits:
            cits = []
        self._cits = set(cits)
            
        
    def resolve(self, pac_id:PAC_ID|str, check_service_status=True, use_issuer_cit=True) -> list[ServiceGroup]:
        '''Resolve a PAC-ID'''
        if isinstance(pac_id, str):
            pac_id_catless = PAC_ID.from_url(pac_id, try_pac_cat=False)
            pac_id = PAC_CAT.from_url(pac_id)
        
        # it's likely to
        if isinstance(pac_id, PAC_ID):
            pac_id_catless = PAC_ID.from_url(pac_id.to_url(), try_pac_cat=False)
        else:
            raise ValueError('pac_id is invalid. Should be a PAC-ID in url form or a PAC-ID object')
    
                
        cits = self._cits.copy()
        if use_issuer_cit:
            if issuer_cit := _get_issuer_cit(pac_id.issuer):
                cits.add(issuer_cit)
         
        matches = []
        for cit in cits:
            if isinstance(cit, CIT_v1):
                # cit v1 has no concept of categories and implied keys. It would treat these segments as value segment
                matches.append(cit.evaluate_pac_id(pac_id_catless))
            else:
                matches.append(cit.evaluate_pac_id(pac_id))
        
        if check_service_status:
            for m in matches:
                m.update_states()   
        return matches
            
    
    
if __name__ == '__main__':
    r = PAC_ID_Resolver()
    r.resolve()
