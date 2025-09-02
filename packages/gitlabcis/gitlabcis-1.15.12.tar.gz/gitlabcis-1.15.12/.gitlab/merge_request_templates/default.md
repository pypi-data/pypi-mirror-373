## Description
<!-- What changes are being introduced? -->

%{first_multiline_commit}

## Checklists

### Requester checklist
<!-- Please ensure the checklist items are complete before requesting a review of this MR-->

Merge request authors, please follow the checklist below:

<details><summary>Requester Checklist</summary>

- If this change modifies [benchmark functions](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/tree/main/gitlabcis/benchmarks?ref_type=heads):
  - The function:
    - [ ] Name matches the `name` of the yaml recommendation
    - [ ] Returns a `dict` containing:
      - `True` or `False` (if the check passed/failed)
      - `None` for skipped checks
      - a `str` with the reason why (e.g. `{None: 'This check requires validation'}`)
    - [ ] The `docstring` contains the id and title of the recommendation to check
  - Limitations:
    - [ ] Any limitations for the function are added to [docs/limitations.md](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/tree/main/docs/limitations.md)
- If this change modifies [recommendations](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/tree/main/gitlabcis/recommendations):
  - [ ] Ensure approval from `CODEOWNERS` is obtained
- [ ] All unit tests pass before requesting review
- [ ] This merge request's title matches the prefixes allowed in `.commitlintrc`
- [ ] Remove _Draft_ phase from the MR

</details>

### MR acceptance checklist
<!-- Please ensure this MR meets the requirements before approving & merging -->

Reviewers, please evaluate this MR against the MR acceptance checklist:

<details><summary>Reviewer Checklist</summary>

- If this change modifies [benchmark functions](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/tree/main/gitlabcis/benchmarks?ref_type=heads):
  - [ ] The function(s) satisfy the recommendation _(see the `audit` section in the yaml file)_
    - i.e. does this function address the recommendation benchmark check
- [ ] This merge request's title matches the prefixes allowed in `.commitlintrc`
- [ ] All tests have passed successfully

</details>

## How to set up and validate locally

To validate changes for this merge request, follow the steps below:

<details><summary>Validation Steps</summary>

`Note`: You only need to complete steps 1-3 once, for future reviews go to `Step 4`.

1. [Install glab](https://gitlab.com/gitlab-org/cli/-/tree/main#installation) (GitLab CLI).
2. [Authenticate to GitLab](https://gitlab.com/gitlab-org/cli/-/tree/main#authentication) using `glab auth login`
3. Clone the repository and enter it:

   ```shell
   # with glab:
   glab repo clone gitlab-security-oss/cis/gitlabcis
   cd gitlabcis

   # or with git:
   git clone git@gitlab.com:gitlab-security-oss/cis/gitlabcis.git
   cd gitlabcis
   ```

4. Checkout the MR:

   ```shell
   # with glab:
   glab mr checkout %{source_branch}

   # or with git:
   git fetch origin merge-requests/%{merge_req_id}/head:%{source_branch}
   git checkout %{source_branch}
   ```

5. Install the modified version of `gitlabcis`:

   ```shell
   make
   ```

6. Validate the change against an input:

   ```sh
   gitlabcis https://gitlab.example.com
   ```

See the [docs](../../docs/readme.md) for more details on usage.

</details>

<!-- commands -->

/assign me
/draft
/label ~"type::Maintenance"
/label ~"release::patch"
/label ~"priority::3"
