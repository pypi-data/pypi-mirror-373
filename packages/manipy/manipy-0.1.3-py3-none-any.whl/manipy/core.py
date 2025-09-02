import functools
import inspect
import torch


def with_manipy(*, no_grad: bool = False, enable_grad: bool = False):
	"""
	Decorator that ensures torch-based functions have 'device' and 'dtype' kwargs.
	- device default: cuda > mps > cpu
	- dtype default: torch.float32
	- Autograd context controlled by decorator args: no_grad / enable_grad (mutually exclusive).
	"""
	if no_grad and enable_grad:
		raise ValueError("no_grad and enable_grad cannot both be True.")

	def _default_device() -> torch.device:
		if torch.cuda.is_available():
			return torch.device("cuda")
		# Guard for environments without MPS backend
		if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
			return torch.device("mps")
		return torch.device("cpu")

	def decorator(fn):
		sig = inspect.signature(fn)
		has_varkw = any(p.kind == p.VAR_KEYWORD for p in sig.parameters.values())
		accepts_device = "device" in sig.parameters or has_varkw
		accepts_dtype = "dtype" in sig.parameters or has_varkw

		@functools.wraps(fn)
		def wrapper(*args, **kwargs):
			# Normalize/assign device
			if accepts_device:
				if "device" not in kwargs or kwargs["device"] is None:
					kwargs["device"] = _default_device()
				else:
					if not isinstance(kwargs["device"], torch.device):
						kwargs["device"] = torch.device(kwargs["device"])
			else:
				kwargs.pop("device", None)

			# Normalize/assign dtype
			if accepts_dtype:
				if "dtype" not in kwargs or kwargs["dtype"] is None:
					kwargs["dtype"] = torch.float32
				else:
					# Accept only torch.dtype or None; convert simple strings if provided
					if isinstance(kwargs["dtype"], str) and hasattr(torch, kwargs["dtype"]):
						kwargs["dtype"] = getattr(torch, kwargs["dtype"])
			else:
				kwargs.pop("dtype", None)

			# Autograd context
			if no_grad:
				with torch.no_grad():
					return fn(*args, **kwargs)
			if enable_grad:
				with torch.enable_grad():
					return fn(*args, **kwargs)
			return fn(*args, **kwargs)

		return wrapper

	return decorator