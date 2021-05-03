from google.cloud import automl_v1beta1


# 'content' is base-64-encoded image data.
def get_prediction(file_path):
    with open(file_path, 'rb') as ff:
        content = ff.read()
    project_id = "672800348011"
    model_id = "ICN4261678481957453824"
    prediction_client = automl_v1beta1.PredictionServiceClient()

    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content}}
    params = {}
    request = prediction_client.predict(name=name, payload=payload, params=params)
    return request  # waits till request is returned
