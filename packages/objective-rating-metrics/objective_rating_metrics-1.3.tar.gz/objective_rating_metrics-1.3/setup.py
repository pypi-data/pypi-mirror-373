from setuptools import setup, find_packages

def main():
    setup(name='objective_rating_metrics',
          version='1.3',
          url='https://openvt.eu/validation-metrics/ISO18571',
          description='Python implementation of ISO/TS 18571',
          author='VSI TU Graz',
          author_email='vsi.office@tugraz.at',
          python_requires='>=3.8',
          packages=find_packages(),
          install_requires=[
              'pyyaml',
              'pillow',
              'jsonschema',
              'ordered-set',
              'certifi',
              'shapely',
              'numpy',
              'pandas',
              'dtwalign'
          ])


if __name__ == '__main__':
    main()
