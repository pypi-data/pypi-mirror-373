# Changelog

## [0.17.0](https://gitlab.com/marge-org/marge-bot/compare/0.16.1...0.17.0) (2025-09-01)

### Features

* Add support for signing commits ([1d94039](https://gitlab.com/marge-org/marge-bot/commit/1d9403962a116e88018ff90ad5aeaa314a79f074))

### Bug Fixes

* **git:** add FILTER_BRANCH so the bot does not wait 10 seconds ([30114b8](https://gitlab.com/marge-org/marge-bot/commit/30114b82dd140d7af2307cb30be708a1363378a6)), closes [#426](https://gitlab.com/marge-org/marge-bot/issues/426)

## [0.16.1](https://gitlab.com/marge-org/marge-bot/compare/0.16.0...0.16.1) (2025-07-01)

### Bug Fixes

* **git:** use --force-with-lease to avoid the bug described in [#435](https://gitlab.com/marge-org/marge-bot/issues/435) ([8e84a9f](https://gitlab.com/marge-org/marge-bot/commit/8e84a9f856c5ff598f0829de9f09efda9e4d5be1))

## [0.16.0](https://gitlab.com/marge-org/marge-bot/compare/0.15.3...0.16.0) (2025-06-01)

### Features

* Add new config --keep-committer ([3fb8ab7](https://gitlab.com/marge-org/marge-bot/commit/3fb8ab74b8781505530c21a28ac08080bc7deedb))

### Bug Fixes

* Pass sudo as a keyword argument when impersonating ([48cf1a2](https://gitlab.com/marge-org/marge-bot/commit/48cf1a23ba0bc320bf48a74f3f8132faec4d23e7))
* Pluralize committers in the codebase ([46cab14](https://gitlab.com/marge-org/marge-bot/commit/46cab14cf9fae6b41dc76fea3a83763ee281324a))

## [0.15.3](https://gitlab.com/marge-org/marge-bot/compare/0.15.2...0.15.3) (2025-04-15)

### ⚠ BREAKING CHANGES

* Adapt to upstream status code change for non-mergeable MRs

### Bug Fixes

* Adapt to upstream status code change for non-mergeable MRs ([d122482](https://gitlab.com/marge-org/marge-bot/commit/d12248267190436f00fa5681c08dd7128eeb9854))
* Pull https auth handling into Repo class ([f86a933](https://gitlab.com/marge-org/marge-bot/commit/f86a933ec12fc33311d4b9a0119d1feae0b83c58)), closes [#408](https://gitlab.com/marge-org/marge-bot/issues/408)

## [0.15.2](https://gitlab.com/marge-org/marge-bot/compare/0.15.1...0.15.2) (2025-03-15)

### Bug Fixes

* set marge-bot user home in Dockerfile ([2249108](https://gitlab.com/marge-org/marge-bot/commit/2249108adf01d1360f795d4b767c0081a4a89986))

## [0.15.1](https://gitlab.com/marge-org/marge-bot/compare/0.15.0...0.15.1) (2025-03-01)

### Bug Fixes

* **deps:** update all non-major dependencies ([27e71dc](https://gitlab.com/marge-org/marge-bot/commit/27e71dc70e79736a661351be20c02a6f75f6be9d))

## [0.15.0](https://gitlab.com/marge-org/marge-bot/compare/0.14.2...0.15.0) (2025-02-15)

### Features

* make Marge messages more user-friendly ([c7a9780](https://gitlab.com/marge-org/marge-bot/commit/c7a9780dc2c397138d75ccc67c813d8d833c6d5a))

## [0.14.2](https://gitlab.com/marge-org/marge-bot/compare/0.14.1...0.14.2) (2025-02-01)

### Bug Fixes

* **deps:** update all non-major dependencies ([8a7d380](https://gitlab.com/marge-org/marge-bot/commit/8a7d380c36e79249bcbb9e7aff2a6ed589154108))
* **helm:** change mountPoint to mountPath in k8s deployment ([15a5780](https://gitlab.com/marge-org/marge-bot/commit/15a5780dfab735ba1decedaa9fb45cbb2f5fd947))
* typos in helm ([dd51443](https://gitlab.com/marge-org/marge-bot/commit/dd51443ba6572b9663a96ae490e0abdb07da232f))

## [0.14.1](https://gitlab.com/marge-org/marge-bot/compare/0.14.0...0.14.1) (2025-01-01)

### Bug Fixes

* **deps:** update all non-major dependencies ([0b18171](https://gitlab.com/marge-org/marge-bot/commit/0b18171293890633ca0e3b323964208aa3ca42f2))
* **deps:** update all non-major dependencies ([4742859](https://gitlab.com/marge-org/marge-bot/commit/4742859fa609dc069c3ef949a91aeb7fce857a64))

## [0.14.0](https://gitlab.com/marge-org/marge-bot/compare/0.13.0...0.14.0) (2024-12-15)

### Features

* Don't run optional manual jobs automatically ([61732a5](https://gitlab.com/marge-org/marge-bot/commit/61732a54c964b0d0ec95915e921feeae23faca22))

### Bug Fixes

* Ensure fetches from forked repos are also blobless ([cca1d2a](https://gitlab.com/marge-org/marge-bot/commit/cca1d2ab26638022d6befb3cd12f55f9c279bc42))
* **single_merge_job:** add git timeout comments ([bb6a5ad](https://gitlab.com/marge-org/marge-bot/commit/bb6a5ad11cae3b0b7c947905196e3f32478a2e7e))

## [0.13.0](https://gitlab.com/marge-org/marge-bot/compare/0.12.0...0.13.0) (2024-12-01)

### Features

* Handle manual pipelines ([ad31d3d](https://gitlab.com/marge-org/marge-bot/commit/ad31d3d2f9ad334712a466f2300e8a972dcd52a7))

### Bug Fixes

* Explicitly handle 'canceling' status ([27d496c](https://gitlab.com/marge-org/marge-bot/commit/27d496c45c3fe22e6fa7d889688892cb5d3d9a0f))
* Rebase when MR status is 'need_rebase' ([0411a44](https://gitlab.com/marge-org/marge-bot/commit/0411a44096fc8206f931f7c0eff3dc62204b2894)), closes [#353](https://gitlab.com/marge-org/marge-bot/issues/353)
* Skip processing of archived projects ([29a7689](https://gitlab.com/marge-org/marge-bot/commit/29a7689aa7c24bfd843c245a8147a00b606b7027)), closes [#208](https://gitlab.com/marge-org/marge-bot/issues/208)

## [0.12.0](https://gitlab.com/marge-org/marge-bot/compare/0.11.0...0.12.0) (2024-11-24)

### Features

* Add hook for customizing pipeline message ([30ed97e](https://gitlab.com/marge-org/marge-bot/commit/30ed97e231823339b52cab58f9c53fb772c2ee10))
* **build:** publish pypi package ([d5864e4](https://gitlab.com/marge-org/marge-bot/commit/d5864e42ca45cb9bb1c4bbbb9939903d3f5c3140))
* Enable partial blobless clones ([9ec40b5](https://gitlab.com/marge-org/marge-bot/commit/9ec40b54552e51877af89c126d3bb5bf1ed5d79b)), closes [#319](https://gitlab.com/marge-org/marge-bot/issues/319) [#398](https://gitlab.com/marge-org/marge-bot/issues/398)
* return pipeline_id from get_mr_ci_status ([4464766](https://gitlab.com/marge-org/marge-bot/commit/44647669d68ee7567276b19647b401c9ebc1ea80))

## [0.11.0](https://gitlab.com/marge-org/marge-bot/compare/0.10.1...0.11.0) (2024-11-21)

### Bug Fixes

* **deps:** update all non-major dependencies ([3bd96b0](https://gitlab.com/marge-org/marge-bot/commit/3bd96b04fff9458717ca1eaa000025e3c5da7de9))
* **deps:** update dependency python-gitlab to v5 ([bb6132f](https://gitlab.com/marge-org/marge-bot/commit/bb6132fea147e0074f79a0cc1e96cd4916cf8ca2))
* Do not install unspecified dependencies from requirements.txt ([caee886](https://gitlab.com/marge-org/marge-bot/commit/caee8867051a75d773395a5f869b3f053f99d97b))
* Replace broken call to `has_calls` with `assert_has_calls` ([2e93a5e](https://gitlab.com/marge-org/marge-bot/commit/2e93a5e9232886a1fff5db561b52faf43f563e6e))
* update poetry version to unbreak docker build ([22bec67](https://gitlab.com/marge-org/marge-bot/commit/22bec67649c78355b70f13e49253fab83b33d0b7))
* Use include_rebase_in_progress in rebase API ([1eb8e32](https://gitlab.com/marge-org/marge-bot/commit/1eb8e3286ddcf3de0c5f4b340a00d49e0b51b4c5))
* Use python-gitlab for HTTP requests ([8a3442a](https://gitlab.com/marge-org/marge-bot/commit/8a3442a06eb2d0a7dfdd78263d871a0711c32ddf)), closes [#126](https://gitlab.com/marge-org/marge-bot/issues/126) [#144](https://gitlab.com/marge-org/marge-bot/issues/144)

### Features

* provide ARM64 images ([76f38c1](https://gitlab.com/marge-org/marge-bot/commit/76f38c14c6841c9aba8633ad5bd02e5fef729c76))
* Switch to Merge Requests API to fetch assigned MRs ([5becc7d](https://gitlab.com/marge-org/marge-bot/commit/5becc7da307bf53792d3daf603b29e77a2b04c8a)), closes [#97](https://gitlab.com/marge-org/marge-bot/issues/97)

## [0.10.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.10.1)

### Features

* Guarantee pipeline before merging

## [0.10.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.10.0)

### Features

* Feature: implement HTTPS support for cloning (#225) #283
* Feature: Make CI work with GitHub Actions #308
* Feature: Allow running marge-bot in CI pipelines or as a single CLI job #289
* Fix: Bump urllib3 from 1.26.4 to 1.26.5 #310
* Fix: Bump urllib3 from 1.26.3 to 1.26.4 #306
* Fix: Upgrade dependencies and fix lints and tests #305
* Fix: AccessLevel enum matches GitLab docs #294

## [0.9.5](https://gitlab.com/marge-org/marge-bot/-/tags/0.9.5)

### Features

* Feature: Add new choice `assigned_at` to option `merge_order` #268
* Fix: Wait for merge status to resolve #265

## [0.9.4](https://gitlab.com/marge-org/marge-bot/-/tags/0.9.4)

* Fix: handle `CannotMerge` which could be raised from `update_merge_request` #275
* Fix: maintain `batch_mr_sha` value when batch merging with fast forward commits #276

## [0.9.3](https://gitlab.com/marge-org/marge-bot/-/tags/0.9.3)

### Features

* allow merge commits in batch MRs, to make the commits be exactly the same in
      the sub MRs and the batch MR. Add `--use-merge-commit-batches` and `--skip-ci-batches` options #264
* add `--use-no-ff-batches` to disable fast forwarding of batch merges (#256, #259)

## [0.9.2](https://gitlab.com/marge-org/marge-bot/-/tags/0.9.2)

* Fix: ensure parameters are correct when merging with/without pipelines enabled #251
* Fix: only delete source branch if forced #193
* Fix: fix sandboxed build #250

## [0.9.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.9.1)

### Features

* support passing a timezone with the embargo #228
* Fix: fix not checking the target project for MRs from forked projects #218

## [0.9.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.9.0)

### Features

* support rebasing through GitLab's API #160
* allow restrict source branches #206
* Fix: only fetch projects with min access level #166
* Fix: bump all dependencies (getting rid of vulnerable packages) #179
* Fix: support multiple assignees #186, #192
* Fix: fetch pipelines by merge request instead of branch #212
* Fix: fix unassign when author is Marge #211
* Enhancement: ignore archived projects #177
* Enhancement: add a timeout to all gitlab requests #200
* Enhancement: smaller docker image size  #199

## [0.8.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.8.1)

### Features

* allow merging in order of last-update time #149

## [0.8.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.8.0)

### Features

* allow reference repository in git clone #129
* add new stable/master tags for docker images #142
* Fix: fix TypeError when fetching source project #122
* Fix: handle CI status 'skipped' #127
* Fix: handle merging when source branch is master #127
* Fix: handle error on pushing to protected branches #127
* Enhancement: add appropriate error if unresolved discussions on merge request #136
* Enhancement: ensure reviewer and commit author aren't the same #137

## [0.7.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.7.0)

### Features

* add `--batch` to better support repos with many daily MRs and slow-ish CI (#84, #116)
* Fix: fix fuse() call when using experimental --use-merge-strategy to update source branch #102
* Fix: Get latest CI status of a commit filtered by branch #96 (thanks to benjamb)
* Enhancement: Check MR is mergeable before accepting MR #117 

## [0.6.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.6.1)

* Fix when target SHA is retrieved #92.
* Replace word "gitlab" with "GitLab" #93.

## [0.6.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.6.0)

* Fix issue due to a `master` branch being assumed when removing
      local branches #88.
* Better error reporting when there are no changes left
      after rebasing #87.
* Add --approval-reset-timeout option #85.
* Fix encoding issues under Windows #86.
* Support new merge-request status "locked" #79.
* Fixes issue where stale branches in marge's repo could
      lead to conflicts #78.
* Add experimental --use-merge-strategy flag that uses merge-commits
      instead of rebasing (#72, and also #90 for caveats).

## [0.5.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.5.1)

* Sleep even less between polling for MRs #75.

## [0.5.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.5.0)

* Added "default -> config file -> env var -> args" way to configure marge-bot #71

## [0.4.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.4.1)

* Fixed bug in error handling of commit rewriting (#70 / 1438867)
* Add --project-regexp argument to restrict to certain target branches $65.
* Sleep less between merging requests while there are jobs pending #67.
* Less verborragic logging when --debug is used #66.

## [0.4.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.4.0)

* The official docker image is now on `smarkets/marge-bot` not (`smarketshq/marge-bot`).
* Add a --add-part-of option to tag commit messages with originating MR #48.
* Add a --git-timeout parameter (that takes time units); also add --ci-timeout
      that deprecates --max-ci-time-in-minutes #58.
* Re-approve immediately after push #53.
* Always use --ssh-key-file if passed (never ssh-agent or keys from ~/.ssh) #61.
* Fix bad LOCALE problem in official image (hardcode utf-8 everywhere) #57.
* Don't blow up on logging bad json responses #51.
* Grammar fix #52.

## [0.3.2](https://gitlab.com/marge-org/marge-bot/-/tags/0.3.2)

Fix support for branches with "/" in their names #50.

## [0.3.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.3.1)

Fix start-up error when running as non-admin user #49.

## [0.3.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.3.0)

* Display better messages when GitLab refuses to merge #32, #33.
* Handle auto-squash being selected #14.
* Add `--max-ci-time-in-minutes`, with default of 15 #44.
* Fix clean-up of `ssh-key-xxx` files #38.
* All command line args now have an environment var equivalent #35.

## [0.2.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.2.0)

* Add `--project-regexp` flag, to select which projects to include/exclude.
* Fix GitLab CE incompatibilities #30.

## [0.1.2](https://gitlab.com/marge-org/marge-bot/-/tags/0.1.2)

### Fixes

* Fix parsing of GitLab versions #28.

## [0.1.1](https://gitlab.com/marge-org/marge-bot/-/tags/0.1.1)

### Fixes

* failure to take into account group permissions #19.

## [0.1.0](https://gitlab.com/marge-org/marge-bot/-/tags/0.1.0)

Initial release.
