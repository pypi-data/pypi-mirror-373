import setuptools

with open('README.md', 'r') as fh:
  long_description = fh.read()

setuptools.setup(
  name = 'augmed',
  packages = setuptools.find_packages(),
  version = '0.0.1',
  description = 'Data augmentation for medical imaging with PyTorch',
  long_description = long_description,
  author = 'Brett Clark',
  author_email = 'clarkbab@gmail.com',
  url = 'https://github.com/clarkbab/augmed',
  keywords = ['data augmentation', 'medical imaging', 'pytorch'],
  classifiers = []
)

