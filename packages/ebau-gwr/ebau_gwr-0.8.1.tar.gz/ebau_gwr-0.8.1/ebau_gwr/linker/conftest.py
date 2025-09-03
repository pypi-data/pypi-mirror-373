import hashlib
import uuid

import pytest


@pytest.fixture()
def deterministic_uuids(mocker):
    # md5 hex digests are the same length as UUIDs, so django happily accepts
    # them.  Note also this has no cryptographic use here, so md5 is totally
    # fine
    hashy = hashlib.md5()

    def next_uuid():
        # add some string to the hash. This modifies it enough to yield a
        # totally different value
        hashy.update(b"x")
        # format: 9336ebf2-5087-d91c-818e-e6e9 ec29 f8c1
        # lengths: 8        4    4    4    12
        digest = hashy.hexdigest()
        return uuid.UUID(
            "-".join(
                [
                    digest[:8],  # 8
                    digest[8:12],  # 4
                    digest[12:16],  # 4
                    digest[16:20],  # 4
                    digest[20:],  # 4
                ]
            )
        )

    mocker.patch("uuid.uuid4", next_uuid)
