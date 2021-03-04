"""
    visor_db_api
    This provides an api for the common operations of the visor_db

"""
import visor_model
import uuid
import datetime


class VisorDatabaseAPI:

    def __init__(self, db_url):
        self.session = visor_model.create_db_session(db_url)

    #
    # VisorSession
    #
    def create_new_session(self, user_token, client_string=None) -> visor_model.VisorSession:
        session_id = uuid.uuid4().hex
        visor_session = visor_model.VisorSession(session_id=session_id,
                                                 client_string=client_string,
                                                 user_token=user_token,
                                                 start_time=datetime.datetime.utcnow())
        self.session.add(visor_session)
        self.session.commit()

        return visor_session

    # def lookup_session_by_id(self, session_id) -> visor_model.VisorSession:
    #     visor_session = self.session.query(visor_model.VisorSession)\
    #                         .filter(visor_model.VisorSession.session_id == session_id)\
    #                         .one()

    #     return visor_session

    def close_session_by_id(self, session_id):
        visor_session = self.lookup_session_by_id(session_id)
        visor_session.end_time = datetime.datetime.utcnow()
        self.session.commit()

    #
    # VisorSessionRecord
    #
    def create_new_session_record(self, session_id, image_path=None) -> visor_model.VisorSessionRecord:
        session_record = visor_model.VisorSessionRecord(session_id=session_id,
                                                        upload_state="failed",
                                                        image_path=image_path)
        self.session.add(session_record)
        self.session.commit()
        return session_record

    def lookup_session_record_by_id(self, record_id) -> visor_model.VisorSessionRecord:
        visor_session_record = self.session.query(visor_model.VisorSessionRecord)\
            .filter(visor_model.VisorSessionRecord.record_id == record_id)\
            .one()

        return visor_session_record

    def lookup_all_session_records_by_session_id(self, session_id) -> [visor_model.VisorSessionRecord]:
        visor_session_records = self.session.query(visor_model.VisorSessionRecord)\
            .filter(visor_model.VisorSessionRecord.session_id == session_id)\
            .all()

        return visor_session_records

    def update_session_record_by_record_id(self, record_id, upload_state=None, image_id=None, image_path=None):
        record = self.lookup_session_record_by_id(record_id)
        changed = False
        if upload_state is not None:
            changed = True
            record.upload_state = upload_state

        if image_id is not None:
            changed = True
            record.image_id = image_id

        if image_path is not None:
            changed = True
            record.image_path = image_path

        if changed:
            self.session.commit()

    #
    #   VisorImage
    #
    def create_new_image(self, session_id, s3_key="{image_id}", crc=None, image_path=None) -> visor_model.VisorImage:
        new_uuid = str(uuid.uuid4())
        image_obj = visor_model.VisorImage(image_id=new_uuid,
                                           session_id=session_id,
                                           s3_key=s3_key.format(
                                               image_id=new_uuid),
                                           crc=crc,
                                           image_path=image_path,
                                           upload_time=datetime.datetime.utcnow()
                                           )
        self.session.add(image_obj)
        self.session.commit()
        return image_obj

    def lookup_image_by_image_id(self, image_id) -> visor_model.VisorImage:
        visor_image = self.session.query(visor_model.VisorImage)\
            .filter(visor_model.VisorImage.image_id == image_id)\
            .one()

        return visor_image

    def lookup_all_images_by_session_id(self, session_id) -> [visor_model.VisorImage]:
        visor_image = self.session.query(visor_model.VisorImage)\
            .filter(visor_model.VisorImage.session_id == session_id)\
            .all()

        return visor_image

    def create_new_image_with_image_object(self, image_object) -> visor_model.VisorImage:
        self.session.add(image_object)
        self.session.commit()
        return image_object

    # // we dont need this   call create_new_session_record, update_session_record_by_record_id

    def upload_state_with_session_object(self, upload_object) -> visor_model.VisorSessionRecord:
        self.session.add(upload_object)
        self.session.commit()
        return upload_object

    def lookup_image_by_crc(self, crc) -> visor_model.VisorImage:
        visor_image = self.session.query(visor_model.VisorImage)\
            .filter(visor_model.VisorImage.crc == crc)\
            .one()

        return visor_image

    def update_image_by_image_id(self, image_id, s3_key=None, crc=None, image_path=None):
        visor_image = self.lookup_image_by_image_id(image_id)

        changed = False

        if s3_key is not None:
            changed = True
            visor_image.s3_key = s3_key.format(
                image_id=str(visor_image.image_id))

        if crc is not None:
            changed = True
            visor_image.crc = crc

        if image_path is not None:
            changed = True
            visor_image.image_path = image_path

        if changed:
            self.session.commit()
