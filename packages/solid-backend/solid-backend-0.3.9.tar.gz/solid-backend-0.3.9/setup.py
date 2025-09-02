# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['solid_backend',
 'solid_backend.contact',
 'solid_backend.contact.migrations',
 'solid_backend.contact.tests',
 'solid_backend.contact.tests.conftest_files',
 'solid_backend.content',
 'solid_backend.content.migrations',
 'solid_backend.content.tests',
 'solid_backend.content.tests.conftest_files',
 'solid_backend.glossary',
 'solid_backend.glossary.migrations',
 'solid_backend.glossary.tests',
 'solid_backend.glossary.tests.conftest_files',
 'solid_backend.media_object',
 'solid_backend.media_object.migrations',
 'solid_backend.media_object.tests',
 'solid_backend.media_object.tests.conftest_files',
 'solid_backend.message',
 'solid_backend.message.migrations',
 'solid_backend.message.tests',
 'solid_backend.message.tests.conftest_files',
 'solid_backend.openzoom',
 'solid_backend.photograph',
 'solid_backend.photograph.migrations',
 'solid_backend.photograph.tests',
 'solid_backend.photograph.tests.conftest_files',
 'solid_backend.quiz',
 'solid_backend.quiz.migrations',
 'solid_backend.quiz.tests',
 'solid_backend.quiz.tests.conftest_files',
 'solid_backend.slideshow',
 'solid_backend.slideshow.migrations',
 'solid_backend.slideshow.tests',
 'solid_backend.slideshow.tests.conftest_files',
 'solid_backend.utils']

package_data = \
{'': ['*'],
 'solid_backend.media_object': ['static/media_object/css/*',
                                'static/media_object/js/*',
                                'templates/media_object/*'],
 'solid_backend.quiz': ['static/quiz/js/*']}

install_requires = \
['django-cleanup==4.0.0',
 'django-filter>=21.1,<22.0',
 'django-mptt==0.11.0',
 'django-stdimage>=5.1.1,<6.0.0',
 'django-taggit>=1.5.1,<2.0.0',
 'django>=3.0.7,<4.0.0',
 'djangorestframework==3.11.0',
 'mutagen>=1.44.0,<2.0.0',
 'pillow==7.1.2',
 'psycopg2-binary>=2.8.5,<3.0.0']

setup_kwargs = {
    'name': 'solid-backend',
    'version': '0.3.9',
    'description': 'Clean Django app for e-learning application with...',
    'long_description': '# S.O.L.I.D.-Backend\n\n<p align="center">\n<a href="https://codecov.io/gh/zentrumnawi/solid-backend">\n  <img src="https://codecov.io/gh/zentrumnawi/solid-backend/branch/master/graph/badge.svg" /> \n</a>\n<a href="https://travis-ci.com/zentrumnawi/solid-backend"> \n  <img src="https://travis-ci.com/zentrumnawi/solid-backend.svg?branch=master">\n</a>\n<a href="https://github.com/ambv/black">\n  <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">\n</a>\n</p>\n\n## What is S.O.L.I.D.?\nThe project\'s name is an acronym for **S**ystematic **O**bject-**L**earning and **I**dentification, \nwhich is the purpose of this pluggable django app. It is here to provide a solid (hehe - :D) foundation for future eLearning apps.\nDuring the creation of two eLearning apps at Goethe University Frankfurt we figured out that a lot of disciplines require students to learn how to systematically analyse and classify certain objects. Those objects might be hand-samples of minerals, stones, stuffed animals, paintings or plants, mostly stored in archives with limited access - or none at all. To prevent us from repeating all steps in the creation of a back- and frontend, we focused on the question "Which components will all these apps have in common?" and this package is what we came up with.\nIn order to tackle the problem of limited access to hand-samples, we need to store and process high-definition images with the capability of a zoom feature to deliver HD images on any kind of device. Furthermore, we need a way to arrange the hand-samples in a structured way to provide the core feature. But that\'s not it. eLearning does not solely consist of content distribution. So we also thought of a glossary which the students have at hand without the need to refer to the lecture notes. Another module to display miscellaneous content is the slideshow feature which dombines text and image on separate pages.\nBeyond that, we implemented a quiz in order to give students the opportunity to evaluate their current level of understanding. To top it off, we figured it might be useful to display messages to communicate with our users. Messages can inform about updates, events in the context of a lecture, provide fun facts or make up an advent calender with daily tasks or puzzles. A contact form implementation provides a communication in the other direction.\n\nSo what does S.O.L.I.D provide in short:\n\n- A generic way to set up database models which can be structured in a hierarchical tree.\n- A simple way to store high-definition images which provides automatic creation of DZI-files for the usage of [OpenSeadragon](https://openseadragon.github.io/)\n- A Quiz-system with a variety of Question types.\n- A Glossary to provide subject-specific terminology.\n- A Message system which can be utilized in various ways.\n- A Slideshow system to provide content in a presentation style.\n- A Feedback form to facilitate bug reports and questions.\nSo if you are looking to build the backend of an eLearning app, you came to the right place.\nFor inspiration or just to see what it looks like to use `solid-backend` in the end have a look at [geomat-backend]()and/or [dive-backend]().\nIf you are also interested in the Frontend: We also have an Angular package which can be found [here]() and which is the foundation of the corresponding apps under geomat.uni-frankfurt.de and dive.uni-frankfurt.de\n\n\n## Get started\nRequirements for this package are:\n* Django >3.0.0\n* Djangorestframework 3.11.0\n* django-mptt 0.11.0\n* pillow 7.1.2\n* django-cleanup 4.0.0\n* psycopg2-binary 2.8.5\n* django-taggit 1.5.1\n\nPsycopg2 is important because we are using PostgreSQL specific databasefields. This means that\nyou are also required to use a PostgreSQL database.\n\n### Installation\n\nThe solid-backend package is distributed via PyPi so you can simply install it via\n\t\n\tpip install solid-backend\n\t\nAdd the apps to your `INSTALLED_APPS` for a bare minimum functionality\n\t\n\tsettings.py\n\t\n\tINSTALLED_APPS = [\n    ...,\n    "solid_backend.content",\n    "solid_backend.photograph",\n]\n\nor all apps\n\t\n\tsettings.py\n\t\n\tINSTALLED_APPS = [\n\t\t"solid_backend.contact",\n\t\t"solid_backend.content",\n\t\t"solid_backend.glossary",\n\t\t"solid_backend.message",\n\t\t"solid_backend.quiz",\n\t\t"solid_backend.slideshow",\n\t\t"solid_backend.photograph",\n\t]\n\nAfterwards, don\'t forget to add the url\'s to your url-config.\nHere, again, you can either decide which urls to include or include all of them:\n\nSpecific urls:\n\n\turls.py\n\t\n\turlpatterns = [\n\t\t...,\n\t\turl(r"", include("solid_backend.content.urls"), name="content"),\n\t\turl(r"", include("solid_backend.message.urls"), name="message"),\n\t\turl(r"", include("solid_backend.photograph.urls"), name="photograph"),\n\t\n\t]\n\nAll urls:\n\n\t\turls.py\n\t\n\turlpatterns = [\n\t\t...,\n\t\turl("", include("solid_backend.urls")),\n\t\t\n\t]\n\t\nAfter this you are ready to run the migrations and you are good to go.\n\n\n\n## Documentation\n\nDocumentation is available [here](https://app.gitbook.com/@zentrumnawi/s/dive/).\nThe Documentation is currently only available in german. If you are a non-german speaker\nand want to know more about something feel free to contact us directly via mail and we \nwill figure it out.\n\n## Coverage\n\nComing soon...\n\n## Try it out and local development\n\nFor a How-To guide see the README in the sample_project directory.\n\n',
    'author': 'Christian Grossmüller',
    'author_email': 'chgad.games@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/zentrumnawi/solid-backend',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
