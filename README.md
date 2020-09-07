**Import Words From Reverso***

**Description***

This is an add-on for [Anki][2] - powerful, intelligent flashcards, that makes
remembering things easy via space repetition.

The add-on downloads your dictionary words from [Reverso][3] - a great
free online resource to translate words- and transforms them into Anki cards. 
What makes Reverso very usefull is the Browser plugin that makes it absolutey
no-cost to check the translation of a word. All the words you lookup while
browsing the internet end up in your history in your reverso page and you can
flag them with a star if you really want to remember them.

This plugin lets you import your words into anki.

![screenshot][6]

**Features**

* import history and/or favourites
* can import all elements or just those new (so that it won't overwrite possible
  editing you made)
* can generate reverse card (as in the image where 25 words where found and 50
  cards added to the deck**
* in the card you can click in a link to show the context

**rel 1.0.0 2020-06-06***
initial Release

**rel 1.1.0 2020-06-24***
Changed authentication after change in Reverso login page.
By mistake this version is a copy of 1.0.0. Install next

**rel 1.1.1 2020-06-24 - later...***
Packaging fix

**rel 1.2 2020-06-30***
Added menu entry to add reverse card for Reverso, Fleex and Basic with reverse

**rel 1.3 2020-06-30***
Added check for failed authentication

**rel 1.4 2020-07-14***
Windows: fix for reference to missing get_icon_path function

**rel 1.5 2020-09-05***
Update due to changed Reverso json format, context is now available again.
Template changes:

* question is shown as well when answer is shown
* colors and font to improve readability
* added label to show which translation in reguired (es.: en => it)

**rel 1.5.1 2020-09-05*** Fix in case of first installation

**rel 1.5.2 2020-09-07*** Reverso has template similar to front

**Important Note**
In case of any problems please contact me on the official support page on 
[anki forum][8] or I won't be able to fix it.

**Authors***

Alessandro Dentella for the project [Wikidattica][2]

The layout of the main window was initially copied from [LinguaLeoAnki][5] plugin.

This project is licensed under the GPL License - see the [LICENSE][4] file for details. 


[1]: http://www.reverso.net
[2]: https://apps.ankiweb.net/
[3]: https://www.wikidattica.org
[4]: https://www.gnu.org/licenses/gpl-3.0.html
[5]: https://github.com/vi3itor/lingualeoanki
[6]: https://wikidattica.org/media/ck_uploads/2020/06/07/reverso-animated.gif
[7]: https://ankiweb.net/shared/info/2060267742
[8]: https://forums.ankiweb.net/t/reverso-plugin-official-support-thread/3059
