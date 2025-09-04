# How to contribute
After clone repository

## 1.- Install dependencies
```bash
poetry install
```

## 2.- Run test
```bash
make test
```

## 3.- Run lint
```bash
make lint && make isort
```

## How to publish new version
Once we have done a merge of our Pull request and we have the updated master branch we can generate a new version. For them we have 3 commands that change the version of our library and generate the corresponding tag so that the Bitbucket pipeline starts and publishes our library automatically.

```bash
make release-patch
```

```bash
make release-minor
```

```bash
make release-major
```
