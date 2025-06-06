from app import app, db
from models import Grave, DaftarKematian

def seed_data():
    with app.app_context():
        # Clear existing data
        Grave.query.delete()
        DaftarKematian.query.delete()

        # Add example graves
        graves = [
            Grave(name="John Smith", date_of_birth="1940-05-10", date_of_death="2020-01-15", lot_number="A101", section="North", picture_url="", family_details="Family of John Smith", notes="Beloved father"),
            Grave(name="Mary Johnson", date_of_birth="1935-07-20", date_of_death="2018-11-30", lot_number="B202", section="East", picture_url="", family_details="Family of Mary Johnson", notes="Rest in peace"),
            Grave(name="Robert Brown", date_of_birth="1950-03-12", date_of_death="2019-06-25", lot_number="C303", section="South", picture_url="", family_details="Family of Robert Brown", notes="Forever remembered"),
            Grave(name="Patricia Davis", date_of_birth="1945-09-05", date_of_death="2021-02-10", lot_number="D404", section="West", picture_url="", family_details="Family of Patricia Davis", notes="Loved by all"),
            Grave(name="Michael Wilson", date_of_birth="1938-12-22", date_of_death="2017-08-18", lot_number="E505", section="Central", picture_url="", family_details="Family of Michael Wilson", notes="In loving memory"),
        ]
        db.session.bulk_save_objects(graves)

        # Add example daftar kematian records
        daftar_kematian_records = [
            DaftarKematian(deceased_name="John Smith", stone_number="A101", date_of_birth="1940-05-10", age_at_death=79, heir_name="Anna Smith", heir_contact="123-456-7890"),
            DaftarKematian(deceased_name="Mary Johnson", stone_number="B202", date_of_birth="1935-07-20", age_at_death=83, heir_name="James Johnson", heir_contact="234-567-8901"),
            DaftarKematian(deceased_name="Robert Brown", stone_number="C303", date_of_birth="1950-03-12", age_at_death=69, heir_name="Linda Brown", heir_contact="345-678-9012"),
            DaftarKematian(deceased_name="Patricia Davis", stone_number="D404", date_of_birth="1945-09-05", age_at_death=75, heir_name="David Davis", heir_contact="456-789-0123"),
            DaftarKematian(deceased_name="Michael Wilson", stone_number="E505", date_of_birth="1938-12-22", age_at_death=78, heir_name="Susan Wilson", heir_contact="567-890-1234"),
        ]
        db.session.bulk_save_objects(daftar_kematian_records)

        db.session.commit()
        print("Seed data inserted successfully.")

if __name__ == "__main__":
    seed_data()
