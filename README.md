# RegrabRaceBot
Welcome to the Regrab Race Bot

## Branches
You are currently in the main branch, this is where all major releases should be pushed to and the code you should use unless told otherwise

The dev branch is for any developmental changes being made. This is where values might be set to accomodate only one player, or TTS might be enabled

Any other branches are specific to a change or version and should only be changed with permission from the branch's creator. If in doubt make your own branch.

## Versions
Currently the bot is in pre-alpha. It is mostly nonfunctional, very laggy and has some large bugs. Progression will be based on how complete it is, how many major bugs there are and how it is shared.

vx.x.x (main builds) marks a release. It may not be tested, but should still work

vx.x.xf (f build) means a "final" release of a version. These have been fully tested and are safe to use.

vx.x.xd (d build) is a dev release and should not be used for races unless you are told otherwise.

## TODO
### Features
List of features in order of priority. Red means it affects the program a lot, even if it is a QOL thing.
```diff
+ Log Lap times to the app
+ Log Gate times
+ Make loop more robust
+ Compile the app
+ Search for Quest on network
- Thread the loop/API calls so that it doesn't affect the main app
+ Display the path taken at the end
+ Display the path taken at the end but in 3D
+ Make the app look better
```
### Bugs
Most bugs should go in the issue tracker, but major bugs will be updated here. Red means it is a high priority.
```diff
+ Some gates are not perfectly aligned such as the blue goal
+ Teams and players crash the loop if the values are not perfect
- API call splits up teams into name and values, unsure if this is a python or API error
- Somehow it registered blue team going through two gates while only orange moved through one
```
## How can I help?
Pick something from [## TODO](# TODO) and add it or fix it!

Any help is appreciated, just try to follow the flow outlined above.

Documentation is very appreicated and is a must for f builds, however for certain d builds and main builds it is not always required.
