
import bcrypt
from typing import ByteString

class HashSel:
        """
        Hashage d'un mot de passe avec sel
        """
 
        def __init__(self) -> None:
                """
                Appel du contructeur de la classe de base
                """
                super().__init__()


        @classmethod
        def hasher_sale(cls,mot: str) -> str:
                """
                Hashage du mot avec rajout de sel

                :param mot: mot à hacher avec sel
                :type mot: str
                :return: mot haché
                :rtype: str
                """
                octects: ByteString = mot.encode('utf-8')  
                sel: ByteString = bcrypt.gensalt() 
                return bcrypt.hashpw(octects, sel).decode('utf-8')

        
        @classmethod
        def tester_hash_sale(cls,mot: str,hash: str) -> bool: 

                # checking password
                try:
                        # On encode les deux en utf-8 pour la comparaison bcrypt
                        return bcrypt.checkpw(mot.encode('utf-8'), hash.encode('utf-8'))
                except Exception:
                        return False



if __name__== "__main__":

        
        hash= HashSel.hasher_sale("admin123")

        print(HashSel.tester_hash_sale("admin123",hash))

