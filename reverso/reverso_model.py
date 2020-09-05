from random import randint

from aqt import mw
# from . import utils

collection = mw.col

TEMPLATES = {
    'default': {
        'qfmt': """{{srcText}}<br>
            {{#context}}
	      <br>
              <div class="hint">{{hint:context}} </div> 
              <a class="document" href="{{document}}"><span class="document">{{documentTitle}}</span></a>
        {{/context}}
        <div class="lang">
        {{srcLang}} => {{trgLang}}
        </div>""",
        'afmt': """
            {{srcText}}<hr>
            <p class="translation">
            {{translation}}
            </p>
            <p class="context">
            {{context}}
            </p>
        """
    },
    'reversed': {
        'qfmt': """{{#reverse}}{{translation}}<br>{{/reverse}}
        <div class="lang">
        {{trgLang}} => {{srcLang}}
        </div>
        """,

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
 color: #333;
 background-color: white;
}
.hint, .context {
 font-size: 80%;
 text-align: left;
 font-style: italic;
 color: #132184
}
a.hint {
  color: brown;
  text-align: center;
  font-weight: bold;
  font-style: normal
}
.document, .lang {
   font-size: 70%;
   color: brown;
   position: absolute;
   bottom: 10px;
   right: 10px;
   text-decoration: none;
   text-align: right;
   width: 100%;
}
.lang {
   left: 10px; 
   text-align: left;
}
"""
## This is an old model. It's here just to track that json data from Reverso change...
## the translation{1,2,3} doesn't exist anymore
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
        if self.model:
            self.modify_template()
        # create_model is called from Client.get_model()

    def modify_template(self):
        if self.model['css'] and '.document, .lang' in self.model['css']:
            return
        self.model['css'] = CSS
        self.model['tmpls'][0]['qfmt'] = TEMPLATES['default']['qfmt']
        self.model['tmpls'][0]['afmt'] = TEMPLATES['default']['afmt']
        self.model['tmpls'][1]['qfmt'] = TEMPLATES['default']['qfmt']
        self.model['tmpls'][1]['afmt'] = TEMPLATES['default']['afmt']
        mw.col.models.update(self.model)

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
