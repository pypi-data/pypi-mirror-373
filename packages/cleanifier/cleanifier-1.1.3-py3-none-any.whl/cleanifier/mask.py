from collections import namedtuple

# NOTE: Minimizers are not part of masks. Treat them separately.


# define the Mask class (as a namedtuple)
Mask = namedtuple("Mask", [
    "mask",   # string of # and _
    "tuple",  # tuple of indices of significant positions (#)
    "k",      # weight (number of #)
    "w",      # total width (len(mask))
    "is_contiguous",  # True iff w == k
    ])


def check_mask(mask, symmetric=True, k=0, w=0):
    if not isinstance(mask, str):
        raise TypeError(f"mask must be of type str, not {type(mask)}")
    if symmetric and not mask == mask[::-1]:
        raise ValueError(f"mask '{mask}'' is not symmetric")
    if not (mask[0] == '#' and mask[-1] == '#'):
        raise ValueError(f"first and last characters of mask '{mask}' must be '#'")
    if k > 0 and mask.count('#') != k:
        raise ValueError(f"mask '{mask}' does not have k={k} #s.")
    if w > 0 and len(mask) != w:
        raise ValueError(f"mask '{mask}' does not have width w={w}.")


def _contiguous_string(k):
    return "".join("#" for i in range(k))


def maskstring_to_tuple(mask, symmetric=True):
    check_mask(mask, symmetric=symmetric)
    return tuple([i for i, c in enumerate(mask) if c == '#'])


def tuple_to_maskstring(tmask, symmetric=True):
    w = max(tmask) + 1
    k = len(tmask)
    mask = "".join(['#' if i in tmask else '_' for i in range(w)])
    check_mask(mask, symmetric=symmetric, k=k, w=w)
    return mask


def create_mask(form):
    mask = dict()

    if isinstance(form, int):  # given k: contiguous k-mer
        mask["k"] = form
        mask["w"] = form
        mask["mask"] = mm = _contiguous_string(form)
        mask["tuple"] = maskstring_to_tuple(mm)
    elif isinstance(form, str):  # given string
        mask["mask"] = form
        mask["tuple"] = maskstring_to_tuple(form)
        mask["w"] = len(form)
        mask["k"] = len(mask["tuple"])
    elif isinstance(form, tuple):  # given tuple
        mask["tuple"] = form
        mask["mask"] = tuple_to_maskstring(form)
        mask["w"] = len(mask["mask"])
        mask["k"] = len(form)
    else:
        raise ValueError(f"Wrong input to create_mask: {form=}")

    check_mask(mask["mask"], k=mask["k"], w=mask["w"])
    mask["is_contiguous"] = (mask["k"] == mask["w"])
    return Mask(**mask)
