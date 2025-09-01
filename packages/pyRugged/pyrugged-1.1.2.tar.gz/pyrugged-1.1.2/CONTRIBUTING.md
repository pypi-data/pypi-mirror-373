# PyRugged Contributing guide

Rugged is free software, which means you can use the source code as you wish, without charges, in your applications, and that you can improve it and have your improvements included in the next mainstream release.

# Open Governance

The Rugged project is driven according to an open governance model, involving representatives from different space field actors in a Project Management Committee (PMC).

# Bug report

Any bug should be reported in a github issue.

# Contribution workflow

Contribution requires a Merge Request. 

Rugged workflow is :
* Create an issue (or begin from an existing one)
* Create a Merge Request from the issue: a MR is created accordingly with "Draft:", "Closes xx" and associated "xx-name-issue" branch
* Code your contribution (fully covered by tests) following [Developer manual](./docs/source/developer.rst)
* Push your work on github repository 
* Remove "Draft:" header on merge request when ready

# Releasing

A new release is tagged with its version

1. Push a tag
2. On the pipeline related to the tag, manually trigger the job `py-publish` when available.

