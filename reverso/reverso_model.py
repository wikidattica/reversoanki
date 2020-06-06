from random import randint

from aqt import mw
# from . import utils

collection = mw.col

TEMPLATES = {
    'default': {
        'qfmt': """{{srcText}}<br>
            {{#context}}
              <div class="hint">{{hint:context}}</div> 
              <a class="document" href="{{document}}"><span class="document">{{documentTitle}}</span></a>
        {{/context}}""",

        'afmt': """
            <p class="translation">
            {{translation}}
            </p>
            <p class="context">
            {{context}}
            </p>
        """
    },
    'reversed': {
        'qfmt': """{{#reverse}}{{translation}}<br>{{/reverse}}""",

        'afmt': """
            <p class="translation">
               {{srcText}}
            </p>
            <p class="context">
               {{context}}
            </p>
        """
    }
}
CSS = """.card {
 font-family: arial;
 font-size: 30px;
 text-align: center;
 color: black;
 background-color: white;
}
.hint, .context {
 font-size: 80%
}
.translation {
font-size: 80%
}
.document {
 font-size: 50%;
 color: brown;
 position: absolute;
 bottom: 10px;
 right: 10px;
 text-decoration: none;
 text-align: right;
 width: 100%;
}
    """

#{'id': '876099614',
#  'userid': '439297',
#  'md5': '917f2c2da1acc0c32574841865e8514c',
#  'srcText': 'practitioner',
#  'trgText': '',
#  'srcLang': 'en',
#  'trgLang': 'it',
#  'priority': 0,
#  'creationDate': '2020-01-05T11:35:33Z',
#  'removed': False,
#  'options': '',
#  'status': 3,
#  'translation1': 'medico',
#  'translation2': 'praticante',
#  'translation3': 'operatore',
#  'comment': '',
#  'document': 'https://www.udemy.com/course/docker-mastery/learn/lecture/15518338#overview',
#  'source': 2,
#  'srcContext': "I'm A Practitioner.",
#  'srcSegment': "i'm a practitioner",
#  'documentTitle': 'Docker Mastery: with Kubernetes +Swarm from a Docker Captain | Udemy'},


class ReversoModel:

    NAME = 'Reverso'

    FIELDS = [
        'srcText',
        'translation',
        'context',
        'srcLang',
        'trgLang',
        'comment',
        'documentTitle',
        'document',
        'reverse',  # needed to create possible reversed card
        'id',
    ]
    # def __init__(self):
    # collection non viene visto!!! (None)
    #     self.model = collection.models.byName(self.NAME) or None

    def __init__(self,  deck_name=None):
        self.model = mw.col.models.byName(self.NAME) or None

    def create_model(self):
        self.model = mw.col.models.new(self.NAME)
        self.model['tags'].append(self.NAME)
        self.model['css'] = CSS
        for field in self.FIELDS:
            mw.col.models.addField(self.model, mw.col.models.newField(field))
        val = randint(100000, 1000000)  # Essential for upgrade detection
        self.model['id'] = val
        mw.col.models.update(self.model)
        self.create_templates()
        return self.model

    def create_templates(self):
        for name, info in TEMPLATES.items():
            template = mw.col.models.newTemplate(name)
            template['qfmt'] = info['qfmt']
            template['afmt'] = info['afmt']
            mw.col.models.addTemplate(self.model, template)

        mw.col.models.update(self.model)
