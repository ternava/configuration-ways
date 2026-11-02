+++
title = "ways to configure software"
+++

Most software can be configured, and often in more than one way. In C you use `#ifdef`, in a web app you have a YAML file and some environment variables, and in production you may also have flags. People study each of these separately, but I could not find one place that shows them all.

Using Claude Opus 5.5, I could gather up to 220 ways of configuring software. They are all shown in the figure below, from COBOL's [`CONFIGURATION SECTION`](https://en.wikipedia.org/wiki/COBOL) in 1960 to [`AGENTS.md`](https://agents.md/) in 2025. Time runs from left to right. The rows tell you when each way of configuring software takes effect. Some act while you build the program, others when it starts, and others while it runs.

{{ figure() }}

<p class="caption">The figure was also generated with Claude Opus 5.5. The sources are listed <a href="sources.md">here</a>.</p>
