# cython: language_level=3
import sys

import tritonclient.http as httpclient
from tritonclient.utils import *


model_name = "ai_tools"

with httpclient.InferenceServerClient("localhost:8000") as client:
    inputs = [httpclient.InferInput('INPUT0', [1], "BYTES")]

    input_data = open("example.jpg", 'rb').read()

    # np_input_data = np.asarray([str.encode(input_data)])
    np_input_data = np.asarray([input_data], dtype=object)

    inputs[0].set_data_from_numpy(np_input_data.reshape([1]))

    outputs = [
        httpclient.InferRequestedOutput("OUTPUT0", binary_data=True),
    ]

    response = client.infer(model_name, inputs, request_id=str(1), outputs=outputs)

    result = response.as_numpy('OUTPUT0')
    with open("output.png", "wb") as f:
        f.write(result[0])
    sys.exit(0)
