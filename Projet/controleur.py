import pymysql
import json

class Controleur:

    def __init__(self, db_config):
        self.db = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['db_name'],
            autocommit=True  # commit automatique pour simplifier
        )

    def sauvegarder(self, index, id_type_flux):

        try:
            with self.db.cursor() as cursor:

                sql = """
                INSERT INTO consommation
                (index_consommation, id_sejour, id_type_flux)
                VALUES (%s, 1, 4)
                """

                cursor.execute(sql, (index))
                self.db.commit()

                print(f"Index {index} enregistré (flux {id_type_flux})")

        except Exception as e:
            print("Erreur SQL :", e)

    def process(self, payload):
        try:
            data = json.loads(payload.decode())
            print("JSON reçu OK")

            # Extraction du compteur
            counter_values = data["uplink_message"]["decoded_payload"]["bytes"]["counterValues"]
            index = float(counter_values[0])  # Channel A
            print("Index extrait :", index)

            # Choisir le type de flux correspondant
            id_type_flux = 1
            self.sauvegarder(index, id_type_flux)

        except Exception as e:
            print("Erreur traitement :", e)