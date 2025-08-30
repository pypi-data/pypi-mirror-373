import warnings

# Suppress Pydantic warning about config keys
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2:*")