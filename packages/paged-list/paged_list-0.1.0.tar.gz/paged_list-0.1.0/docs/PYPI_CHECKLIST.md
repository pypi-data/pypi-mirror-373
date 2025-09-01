# PyPI Publishing Checklist for paged-list

This document provides a step-by-step checklist for publishing paged-list to PyPI using Hatch.

## Pre-Publishing Checklist

### 🔧 Setup Requirements

- [ ] **Hatch installed**: `pip install hatch`
- [ ] **PyPI account created**: https://pypi.org/account/register/
- [ ] **Test PyPI account created**: https://test.pypi.org/account/register/
- [ ] **GitHub repository configured** with trusted publishing (optional but recommended)

### 📝 Project Preparation

- [ ] **Version updated** in `paged_list/__init__.py`
- [ ] **CHANGELOG.md updated** with release notes
- [ ] **README.md reviewed** and up-to-date
- [ ] **All tests passing**: `python -m hatch run test`
- [ ] **Code formatted**: `python -m hatch run format`
- [ ] **Linting passed**: `python -m hatch run lint`
- [ ] **Working directory clean**: `git status` shows no uncommitted changes

### 🧪 Testing

- [ ] **Local tests pass**: `python -m hatch run test-cov`
- [ ] **Package builds successfully**: `python -m hatch build`
- [ ] **Test installation works**: Install from dist and test import
- [ ] **Cross-platform tests pass** (via GitHub Actions)

## Publishing Process

### Option 1: Automatic Publishing (Recommended)

1. **Create and push git tag**:

   ```bash
   git tag v0.1.0  # Replace with your version
   git push origin v0.1.0
   ```

1. **Create GitHub release**:

   - Go to https://github.com/christensendaniel/paged-list/releases
   - Click "Create a new release"
   - Select the tag you just created
   - Add release notes
   - Click "Publish release"

1. **GitHub Actions will automatically**:

   - Run tests
   - Build package
   - Publish to PyPI

### Option 2: Manual Publishing

1. **Clean and build**:

   ```bash
   rm -rf dist/
   python -m hatch build
   ```

1. **Test on Test PyPI first**:

   ```bash
   python -m hatch publish -r test
   ```

1. **Verify test installation**:

   ```bash
   pip install -i https://test.pypi.org/simple/ paged-list
   python -c "import paged_list; print(paged_list.__version__)"
   ```

1. **Publish to real PyPI**:

   ```bash
   python -m hatch publish
   ```

## Verification

After publishing, verify the package:

- [ ] **Package appears on PyPI**: https://pypi.org/project/paged-list/
- [ ] **Installation works**: `pip install paged-list`
- [ ] **Import works**: `python -c "from paged_list import PagedList"`
- [ ] **Documentation links work** on PyPI page
- [ ] **Classifier tags are correct** on PyPI page

## Troubleshooting

### Common Issues

**Build fails**:

- Check `pyproject.toml` syntax
- Ensure all files are included in build targets
- Run `python -m hatch build --debug` for verbose output

**Upload fails**:

- Check PyPI credentials
- Ensure version number hasn't been used before
- For "403 Forbidden", check if trusted publishing is configured correctly

**Tests fail**:

- Run tests locally first: `python -m hatch run test`
- Check if all dependencies are specified correctly
- Ensure Python version compatibility

### Authentication

**Using API tokens** (recommended):

1. Generate token at https://pypi.org/manage/account/token/
1. Configure: `hatch config set publish.index.pypi.auth "token"`
1. Store token securely

**Using GitHub trusted publishing** (most secure):

1. Configure on PyPI: https://pypi.org/manage/account/publishing/
1. No manual token management needed
1. GitHub Actions handle authentication automatically

## Post-Publishing Tasks

- [ ] **Update project status** to "Production/Stable" if appropriate
- [ ] **Announce release** on relevant channels
- [ ] **Update documentation** with installation instructions
- [ ] **Monitor for issues** and user feedback
- [ ] **Plan next release** based on feedback

## Quick Commands Reference

```bash
# Development
python -m hatch run test          # Run tests
python -m hatch run test-cov      # Run tests with coverage
python -m hatch run format        # Format code
python -m hatch run lint          # Lint code
python -m hatch run all           # Do everything

# Building
python -m hatch build             # Build package
python -m hatch clean             # Clean build artifacts

# Publishing
python -m hatch publish -r test   # Publish to Test PyPI
python -m hatch publish           # Publish to PyPI

# Version management
python -m hatch version           # Show current version
```

______________________________________________________________________

**Happy Publishing! 🚀**

For questions or issues, refer to:

- [Hatch Documentation](https://hatch.pypa.io/)
- [PyPI Help](https://pypi.org/help/)
- [Packaging User Guide](https://packaging.python.org/)
