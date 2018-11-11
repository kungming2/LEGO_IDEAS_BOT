## About LEGO_IDEAS_BOT

LEGO_IDEAS_BOT is a simple Reddit bot (running under the username [u/LEGO_IDEAS_BOT](https://www.reddit.com/user/LEGO_IDEAS_BOT/overview) that services various Reddit LEGO communities. If a comment includes a [LEGO Ideas set link](https://ideas.lego.com/#all), this bot will reply with simple comment that includes:

* The name of the set
* The author of the set
* An image of the set 
* A short description of the set by its author (3 sentences or 500 words, whichever is shorter)
* How many supporters the set has
* How many days remaning in the set's campaign
* A footer message reminding people to vote for the set if they like it.

#### Origin

This bot was written as a response to a [request of u/rock99rock](https://www.reddit.com/r/RequestABot/comments/619hf8/request_a_bot_that_will_look_for_a_specific_url/) at [r/RequestABot](https://www.reddit.com/r/RequestABot/). I do not frequently update the bot's code as I wrote it at a stage where my Python knowledge was pretty elementary and basic. Rather, I update the bot just enough to maintain compatibility with the site and to correct for any issues that might occur.

The need for the bot originally arose because the main LEGO Ideas site in early 2017 was not mobile-friendly and took incredibly long to load as well. LEGO has since redesigned their Ideas site, so I also reconfigured this bot to provide more information in its comment to retain its utility.

#### Notes

LEGO_IDEAS_BOT is also notably the only Reddit bot that I've written that does not respond to an explicit user command, and instead replies to a pre-determined string (in this case, an Ideas link). However, LEGO_IDEAS_BOT is not a simple "reply bot" like the many novelty comment bots that plague Reddit, as it:

* Has the explicit permission of the mods of the main community it runs on ([r/LEGO](https://www.reddit.com/r/lego/))
* Does not post more than once on the same link per thread
* Does not run on r/all, but rather, only on LEGO-related communities
* Provides useful information in its response
* Contains contact information for its creator in every comment

It is telling, I think, that this bot got several dozen "good bot" comments during the period the bot vote tallier u/GoodBot_BadBot was active, and *not a single* "bad bot" vote. Not that these votes are definitely indicative of anything - they're not - but the LEGO communities have responded positively to LEGO_IDEAS_BOT over the last one-and-a-half years and continue to do so.