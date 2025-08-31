- `Site`
  - build contexts
  - build groups
  - build dependency
  - preprocessors
  - postprocessors
- `Page`
- `Layout`
- `Expandable`s and `Renderable`s
- `RenderNode`

A Site consists of build groups, where each build group contains a list of
Pages, preprocessors, postprocessors, and page dependencies. Each build group
has its own build context. Within a build group, per-page data and Site-global
data can be shared. However, different build groups cannot access data of others.
If you want to share data between build groups, you have to use other means of
shared storage such as external databases or message queues.

This separation of build group allows Ophinode to parallelize the build process.
In site build preparation stage, the main process creates build contexts for each
group. Then it sends the build context to child processes to render the build group.

When `Site.build_site()` is called, the `Site` first creates a `RootBuildContext`
and passes `Site` configurations and `BuildGroup` definitions to `RootBuildContext`.
Then `parallel_build_site(RootBuildContext)` spawns worker processes and each build
group is passed as `BuildContext`.

After each build group finishes rendering, they can return data to `RootBuildContext`
for further processing. The data to return can be controlled by configuring the build
groups. You can copy the entire render data from `BuildContext` to `RootBuildContext`,
or you can write the results in the worker process and return only selected data to
`RootBuildContext`.

## sync vs. parallel
Currently, ophinode support two build strategies, `sync` and `parallel`. They have
important semantic differences when building pages, especially related to context
data updates. Due to this difference, these two strategies can be incompatible if
pages in different `PageGroup`s use same names in `site_data` or even `page_data`.

The biggest difference between `sync` and `parallel` build strategy is that
`sync` allows sharing data between `Site`, `RootBuildContext`, and `BuildContext`
because it does everything inside the main process. If you update `site_data` or
`page_data` inside each `PageGroup`, every other object can see that change.
In `parallel` strategy, however, if a `BuildContext` wants to update the `RootBuildContext`,
the only way to do so is by returning the updates at the end of the page build.

Moreover, `sync` waits other `PageGroup`s when buliding, expanding, and rendering
pages. `PageGroup`s do not proceed to the next stage until others are done working
in the previous one. This differs from `parallel` strategy where each `PageGroup`
proceeds independently of others.
