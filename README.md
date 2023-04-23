# gengem.py
Simple Python script to generate a Gemini gemlog and accompanying Atom feed.
## Required libraries
* [feedgen](https://pypi.org/project/feedgen/)
* That's it 😌

## Usage
### Initial setup
Edit `gengemConfig.cfg` and fill in required information:
* `rootURL` -  The URL where your gemlog is hosted. Only used for permalinks in the Atom feed.
* `gemlogFolder` - The folder where your .txt files containing gemlog posts are stored.
* `public_gemini` - The folder where your `gemlog.gmi` file and `atom.xml` file will be written to. This folder **must** contain a subfolder titled `posts`.

Only the above points are *required* information, but unless you want the title of your gemlog to be "My Gemlog." I highly recommend editing the other fields. The `gengemConfig.cfg` file is commented with usage instructions and examples.
### Executing
Execute `gengem.py` and it will do everything else for you - all your files will be neatly placed in the directory you set as your `public_gemini`. File names are maintained from the `.txt` files (although spaces are replaced with dashes).
#### See it in action!
Download this entire repo and replace the contents of `gengemConfig.cfg` with the contents of `SAMPLE_CONFIG.cfg`. Execute `gengem.py` and.. voila! The sample posts (in the posts directory provided) have been generated into a gemlog, found within the public_gemini folder provided! A gemlog index has also been generated, along with an atom.xml! *Note that this sample atom.xml is pointing to an example.com domain and the links within it **do not work!** This is for demonstration purposes only!*

## Text file format
The first line of your `.txt` files require:
* A title, denoted by a `+title` tag
* A date in ISO 8601 format, denoted by a `+date` tag

Note that the title and date tags can go in any order, so long as they are on the first line of your `.txt` file.
An example `.txt` file:
```
+title My first gemlog! +date 2023-04-21
Hi everyone! This is my first gemlog.
Hope you enjoy!
```