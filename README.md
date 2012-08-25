# Background

I like (and still use) [Trello](http://trello.com) but it wasn't working as a
full GTD system for me. As I'm spending more time in the terminal now and kept
hearing good things, I figured I'd give [Taskwarrior](http://taskwarrior.org/) a shot.

One of the nice things about Trello is that you can take your data with you, so
I attempted to convert from that format to Taskwarrior's.

It took probably longer than it would have if I'd migrated by hand, data entry
style, but it was fun.

This will **probably not work exactly the way you want it to.** Because there's
no clean mapping from Trello ideas to Taskwarrior, you'd have to tune to fit.

# Running it

## Safety first 

You might want to open up `~/.taskrc` and  set
`data.location=/some/temp/place` so you can test importing without messing with
any of your real tasks.

## Let's do this

Once you have a Trello export file, run

        $ ./trello_to_task.py home_board.json out.json
        $ task import out.json

# Customization help

Generally you might want to do different things with board names going to tags,
projects, etc.

Right now

* Everything comes in with `project:home`
* If a card had a checklist on it
    * The name of the card is mashed up (strip spaces and lowercase it)
    * That makes a new project under home (So 'Buy Car' => `home.buycar`)
    * All the checklist items become tasks in that project, as does the
      (originally named) main task itself
    * The main task depends on all the checklist items

## Trello schema notes

The basic structure of the file looks like:

* checklists
    * id, name
    * checkItems
        * id, name, type { check, ... }
* lists
    * id, name, closed
* cards
    * closed
    * idList
    * idChecklists
    * desc
    * name
* actions
    * data
        * text
    * card
        * id
    * type = commentCard

# Taskwarrior format

It's a little easier since it's mostly [well documented](http://taskwarrior.org/projects/taskwarrior/wiki/Json_format).

The strangest thing is the file format doesn't actualy want a list of JSON
objects, it wants one JSON object per line. This makes the whole file not
actually valid JSON, but each line is by itself.
