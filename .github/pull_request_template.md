## Done
- _A changelist description explaining what the change achieves and why you’re making it._

## How to QA
1. Check-out this branch
2. Build this image `docker build . --tag canonicalwebteam/dotrun-image:local`
3. Run this image `docker run -it -p 8004:8004 canonicalwebteam/dotrun-image:local /bin/bash`
4. Run a project
  - `git clone https://github.com/canonical-web-and-design/snapcraft.io/`
  - `cd snapcraft.io`
  - `dotrun`

`dotrun` should install the dependencies and run the project. Once you see this output:
```
Listening at: http://0.0.0.0:8004
```

Visit http://localhost:8004 and check that the website is running.

## Issue / Card
Fixes #
