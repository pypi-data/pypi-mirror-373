"""Core lifespan module providing patchable globals for tests."""

# The streaming tests patch this attribute directly.
reasoning_kernel = None  # type: ignore
