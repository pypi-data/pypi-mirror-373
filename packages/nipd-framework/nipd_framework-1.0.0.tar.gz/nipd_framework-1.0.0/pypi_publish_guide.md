# PyPI Publishing Guide for NIPD Framework

This guide will walk you through the process of packaging and publishing your NIPD Framework to PyPI.

## Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/) and [Test PyPI](https://test.pypi.org/account/register/)
2. **Python 3.13+**: Ensure you have Python 3.13 or higher installed
3. **Required Tools**: Install the necessary packaging tools

```bash
pip install --upgrade pip
pip install --upgrade build twine
```

## Step 1: Prepare Your Package

Your package is already well-structured with:
- [OK] `setup.py` - Package configuration
- [OK] `requirements.txt` - Dependencies
- [OK] `MANIFEST.in` - File inclusion/exclusion rules
- [OK] `README.md` - Package documentation
- [OK] `LICENSE` - License file

## Step 2: Test Your Package Locally

Before publishing, test that your package builds and installs correctly:

```bash
# Clean any previous builds
rm -rf build/ dist/ *.egg-info/

# Build the package
python -m build

# Test installation in a virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate
pip install dist/*.whl

# Test the package
python -c "import nipd; print(nipd.__version__)"
nipd-simulate --help  # Test the console script
```

## Step 3: Test on Test PyPI

Always test on Test PyPI before publishing to the main PyPI:

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ nipd-framework
```

## Step 4: Publish to PyPI

Once you've tested on Test PyPI and everything works:

```bash
# Upload to PyPI
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

## Step 5: Verify Installation

After publishing, verify the package installs correctly:

```bash
# Create a fresh virtual environment
python -m venv fresh_test
source fresh_test/bin/activate  # On Windows: fresh_test\Scripts\activate

# Install from PyPI
pip install nipd-framework

# Test the package
python -c "import nipd; print(nipd.__version__)"
nipd-simulate --help
```

## Package Structure Verification

Your package includes:
- **Core Framework**: `nipd/` directory with all simulation components
- **Pretrained Models**: Final models for each algorithm type
- **Examples**: Usage examples in `examples/` directory
- **Console Script**: `nipd-simulate` command-line interface
- **Documentation**: Comprehensive README with usage examples

## Important Notes

### File Inclusion
The `MANIFEST.in` file ensures:
- [OK] README.md, LICENSE, requirements.txt are included
- [OK] All Python files in `nipd/models/` are included
- [OK] Final pretrained models (`*_final.pt`, `*_final.json`) are included
- [EXCLUDE] Training outputs, simulation results, and intermediate files are excluded
- [EXCLUDE] `__pycache__`, `.pyc`, and other temporary files are excluded

### Dependencies
Your package requires:
- Python 3.13+
- PyTorch, NumPy, Matplotlib, Pandas, NetworkX, and other scientific computing libraries

### License
The package uses CC BY-NC 4.0 license, which is non-commercial. Make sure this aligns with your intentions.

## Troubleshooting

### Common Issues

1. **Package Name Conflict**: If `nipd-framework` is taken, consider alternatives like:
   - `network-ipd-framework`
   - `multi-agent-ipd`
   - `nipd-simulator`

2. **Missing Files**: If files aren't included, check `MANIFEST.in` and ensure they're not excluded

3. **Import Errors**: Test imports in a fresh environment to catch missing dependencies

4. **Console Script Issues**: Ensure the `main` function exists in `nipd.agent_simulator`

### Version Management

To update your package:
1. Update version in `setup.py` and `nipd/__init__.py`
2. Rebuild: `python -m build`
3. Upload: `python -m twine upload dist/*`

## Security Considerations

- Never commit API keys or sensitive data
- Use environment variables for any configuration
- Review all included files before publishing

## Post-Publishing

After successful publication:
1. Update your GitHub repository with the PyPI badge
2. Consider creating a GitHub release
3. Monitor for any issues or feedback
4. Plan for future updates and maintenance

## Useful Commands

```bash
# Check package contents
tar -tzf dist/nipd_framework-*.tar.gz

# Validate package
python -m twine check dist/*

# View package metadata
python setup.py --name --version --description

# Test in isolation
python -m pip install --force-reinstall dist/*.whl
```

## Next Steps

1. **Documentation**: Consider setting up Sphinx documentation
2. **CI/CD**: Set up GitHub Actions for automated testing and publishing
3. **Testing**: Add unit tests and integration tests
4. **Examples**: Create more usage examples and tutorials
5. **Community**: Engage with users and gather feedback

Your package is well-structured and ready for PyPI publication!
