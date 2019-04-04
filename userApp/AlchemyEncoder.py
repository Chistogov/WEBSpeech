from sqlalchemy.ext.declarative import DeclarativeMeta
import json

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)


# @userApp.route('/stats/json')
# def stats_json():
#     logging.info("Stats_Json")
#     pics_by_symp = db.session.query(Symptom.Symptom.symptom_name, Picture.Picture.pic_name, Symptom.Symptom.ear, Symptom.Symptom.throat, Symptom.Symptom.nose, Symptom.Symptom.ismedical)\
#         .join(Recognized.Recognized).filter(Symptom.Symptom.id==Recognized.Recognized.symp_id, Picture.Picture.id==Recognized.Recognized.pic_id)
#     return json.dumps(pics_by_symp.all(), cls=AlchemyEncoder.AlchemyEncoder, ensure_ascii=False).encode('utf8')