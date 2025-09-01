import pickle

from spacy.tokens import Doc, Span


def span_to_doc(span: Span) -> Doc:
    """Covert a span to a doc object.
        Copy all user data and throw an error if this is not possible.

    Args:
        span: The span.

    Returns:
        The document.

    """
    try:
        new_doc = span.as_doc(copy_user_data=True)

        # spacy's built-in `as_doc` does not copy extensions from the doc object;
        # we have to collect them separately
        doc = span.doc
        doc_extensions = {
            attr: getattr(doc._, attr) for attr in dir(doc._) if attr not in ["has", "get", "set"]
        }

        # test whether they are pickleable (if not, they probably contain `Token` or `Span` data;
        # which cannot be copied)
        doc_extensions = pickle.loads(pickle.dumps(doc_extensions))

        # copy the doc extensions
        for key, val in doc_extensions.items():
            setattr(new_doc._, key, val)

        return new_doc
    except NotImplementedError as ex:
        raise NotImplementedError(
            "The slicer cannot copy all of your user data. You should try to include the slicer earlier in the pipeline."
        ) from ex
