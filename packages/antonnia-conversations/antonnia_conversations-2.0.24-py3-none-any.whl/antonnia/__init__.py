# Antonnia namespace package
# This allows multiple antonnia-* packages to be installed and used together

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
