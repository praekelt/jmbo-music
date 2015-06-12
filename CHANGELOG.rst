Changelog
=========

2.0.0
-----
#. Simplify API to use primary keys.
#. Stabilize on Jmbo 2.0.0.

2.0.0a1
-------
#. Update tests.
#. Django 1.6 compatibility.
#. Up minimum jmbo to 2.0.0.

0.2.10
------
#. Expand API to include Track Contributor.

0.2.9
-----
#. Expand the API.

0.2.8
-----
#. Implement an API.

0.2.7
-----
#. Fix tests.
#. Fix possible recursion error when saving a track.

0.2.6
-----
#. Add South dependency on jmbo.

0.2.5
-----
#. Clean up tests.
#. Defensive code to handle tracks wih the same title in scraper.

0.2.4
-----
#. Reinstate last.fm scraping. Scrapers can now be chained.

0.2.3
-----
#. `__unicode__` for track now includes primary contributor.

0.2.2
-----
#. Add index on `last_played` field.

0.2.1
-----
#. Compromise on a foreign key being null so South migration works on legacy database.

0.2
---
#. Refactor credit options to work in a multilingual environment. Existing credit options will be lost but at worst existing UI will have a blank space.
#. Track feed management command framework created. Includes a demo track feed `track_feed_example`.
#. Pull artist, track and album info from Wikipedia.

0.1.2
-----
#. Friendlier urls to detail pages.

0.1.1
-----
#. Rename `get_primary_contributers` method to be `primary_contributors_permitted` property to adhere to Jmbo convention.

0.1
---
#. Introduce a dependency on `jmbo-gallery`, thus implicitly on `jmbo-foundry`.

0.0.7
-----
#. Better packaging.

