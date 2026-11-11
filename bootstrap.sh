#!/usr/bin/env bash
set -euo pipefail

# Prepare local references from the development history on main.
COURSE_URL="${COURSE_URL:-https://github.com/Cyber-TongClass/ToNG-workshop.git}"

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
repo_name() {
    local value="${1%/}"
    value="${value%.git}"
    value="${value#https://github.com/}"
    value="${value#http://github.com/}"
    value="${value#git@github.com:}"
    value="${value#ssh://git@github.com/}"
    printf '%s' "${value,,}"
}

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "Run this script inside your cloned fork."
[[ -z "$(git status --porcelain)" ]] || fail "Your working tree has changes. Save them before running bootstrap."
ORIGIN_URL="$(git remote get-url origin 2>/dev/null)" || fail "No origin remote. Clone your GitHub fork first."
[[ "$(repo_name "$ORIGIN_URL")" != "$(repo_name "$COURSE_URL")" ]] || fail "This is the course repository. Clone your own fork instead."
[[ "$(repo_name "$ORIGIN_URL")" != "cyber-tongclass/tong-workshop" ]] || fail "Clone your own fork, not the course repository."
if git show-ref --verify --quiet refs/heads/submission; then
    fail "A submission branch already exists. Switch to it with: git switch submission"
fi

names=(base native-validation training-logging dataset-loader cpu-parallelism)
shas=(
    2d46a172466f2ecac17bfb670ef79bb58aefa69f
    3a765eb48d38f7edeb9144f90d7b61076dfa279a
    04f98706470772110fab72a67b8765d2929d0d0c
    e80253c288b65f791d3a386202332d1b50c48364
    04f98706470772110fab72a67b8765d2929d0d0c
)

# Fetch only main. Every exercise object must be part of its real history.
git fetch --no-tags "$COURSE_URL" main
main_tip="$(git rev-parse FETCH_HEAD^{commit})"
for i in "${!names[@]}"; do
    actual="$(git rev-parse --verify "${shas[$i]}^{commit}")"
    [[ "$actual" == "${shas[$i]}" ]] || fail "Missing development commit: ${names[$i]}"
    git merge-base --is-ancestor "$actual" "$main_tip" || fail "Commit is not in upstream history: ${names[$i]}"
    destination="refs/remotes/upstream/${names[$i]}"
    if git show-ref --verify --quiet "$destination"; then
        [[ "$(git rev-parse "$destination")" == "$actual" ]] || fail "Conflicting local upstream reference. Use a fresh clone of your fork."
    fi
done
if git remote get-url upstream >/dev/null 2>&1; then
    git remote set-url upstream "$COURSE_URL"
else
    git remote add upstream "$COURSE_URL"
fi
git config --replace-all remote.upstream.fetch '+refs/heads/main:refs/remotes/upstream/main'
git update-ref refs/remotes/upstream/main "$main_tip"
for i in "${!names[@]}"; do
    git update-ref "refs/remotes/upstream/${names[$i]}" "${shas[$i]}"
done
git switch --no-track --create submission upstream/base
printf '\nReady: you are on submission. No changes have been pushed.\n'
printf 'Continue with the setup instructions in README.md.\n'
