# docs

The documentation builder for clearskies and related plugins

## Overview

Each "official" clearskies module (including the core clearskies library itself) has the documentation primarily written in the codebase as docblocks.  The documentation site is then built by extracting these docblocks and stitching them together.  To be clear, this isn't about the low-level "API" documentation that describes every single class/method in the framework.  Rather, this is about the primary documentation site itself (clearskies.info) which is focused on high-level use cases and examples of the primary configuration options.  As a result, it's not a simple matter of just iterating over the classes/methods and building documentation.  To build a coherent documentation site, each plugin has a configuration file that basically outlines the final "structure" or organization of the resulting documentation, as well as the name of a builder class that will combine that configuration information with the codebase itself to create the actual docs.

The docs themselves (in the source code) are all written with markdown.  This documentation builder then takes that markdwon and adds the necessary headers/etc so to make them valid files for [Jekyll](https://jekyllrb.com/), the builder for the current documentation site.  The site itself is hosted in S3, so building an actual documentation site means:

 1. Properly documenting everything inside of the source code via markdown.
 2. Creating a config file (`docs/python/config.json`) to map source code docs to Jekyll files.
 3. Creating a skeleton of a Jekyll site in the `doc/jekyll` folder of the plugin.
 4. Installing this doc builder via `poetry add clear-skies-doc-builder`.
 5. Run the doc builder.
 6. Build with Jekyll.
 7. Push to the appropriate subfolder via S3.
 8. (Only once) Update the main clearskies doc site to know about the new subfolder for this plugin.

Of course, we want the Jekyll sites to be consistent with eachother in terms of style/look.  In the long run we'll probably have this doc builder also bootstrap the Jekyll site, but for now you just have to manually setup the Jekyll build using the main clearskies repo as a template.
