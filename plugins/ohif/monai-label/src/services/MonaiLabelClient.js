/*
Copyright (c) MONAI Consortium
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

import axios from 'axios';

export default class MonaiLabelClient {
  constructor(server_url) {
    this.server_url = new URL(server_url);
  }

  async info() {
    let url = new URL('info', this.server_url);
    return await MonaiLabelClient.api_get(url.toString());
  }

  async segmentation(model, image, params = {}, label = null) {
    // label is used to send label volumes, e.g. scribbles,
    // that are to be used during segmentation
    return this.infer(model, image, params, label);
  }

  async deepgrow(model, image, foreground, background, params = {}) {
    params['foreground'] = foreground;
    params['background'] = background;
    return this.infer(model, image, params);
  }

  async infer(model, image, params, label = null, result_extension = '.nrrd') {
    let url = new URL('infer/' + encodeURIComponent(model), this.server_url);
    url.searchParams.append('image', image);
    url.searchParams.append('output', 'image');
    url = url.toString();

    if (result_extension) {
      params.result_extension = result_extension;
      params.result_dtype = 'uint16';
      params.result_compress = false;
    }

    return await MonaiLabelClient.api_post(
      url,
      params,
      label,
      true,
      'arraybuffer'
    );
  }

  async next_sample(stategy = 'random', params = {}) {
    const url = new URL(
      'activelearning/' + encodeURIComponent(stategy),
      this.server_url
    ).toString();

    return await MonaiLabelClient.api_post(url, params, null, false, 'json');
  }

  async save_label(image, label, params) {
    let url = new URL('datastore/label', this.server_url);
    url.searchParams.append('image', image);
    url = url.toString();
    console.log("save_label",image, label, params,url);
    const data = MonaiLabelClient.constructFormDataFromArray(
      params,
      label,
      'label',
      'label.bin'
    );

    return await MonaiLabelClient.api_put_data(url, data, 'json');
  }

  async login(username, password) {
    let url = new URL(`login`, this.server_url);

    const data = new FormData();
    data.append("username", username);
    data.append("password", password);

    return await MonaiLabelClient.api_post_data(url, data, 'json');
  }

  async register(username, password,email,name) {
    let url = new URL(`register`, this.server_url);

    const data = new FormData();

    const result = {
      "username": username,
      "password": password,
      "email": email,
      "full_name": name,
      "scopes": "admin"
    }
    data.append("username", username);
    data.append("password", password);
    data.append("email", email);
    data.append("full_name", name);
    data.append("scopes", 'admin');

    return await MonaiLabelClient.api_post_data(url, result, 'json');
  }

  async list_users() {
    let url = new URL('users', this.server_url);
    return await MonaiLabelClient.api_get(url.toString());
  }

  async delete_user(id) {
    const url = new URL('users', this.server_url).toString().concat(`/${id}`);

    return await MonaiLabelClient.api_delete(url);
  }

  async is_train_running() {
    let url = new URL('train', this.server_url);
    url.searchParams.append('check_if_running', 'true');
    url = url.toString();

    const response = await MonaiLabelClient.api_get(url);
    return (
      response && response.status === 200 && response.data.status === 'RUNNING'
    );
  }

  async run_train(params) {
    const url = new URL('train', this.server_url).toString();
    return await MonaiLabelClient.api_post(url, params, null, false, 'json');
  }

  async stop_train() {
    const url = new URL('train', this.server_url).toString();
    return await MonaiLabelClient.api_delete(url);
  }

  static constructFormDataFromArray(params, data, name, fileName) {
    let formData = new FormData();
    formData.append('params', JSON.stringify(params));
    formData.append(name, data, fileName);
    return formData;
  }

  static constructFormData(params, files) {
    let formData = new FormData();
    formData.append('params', JSON.stringify(params));

    if (files) {
      if (!Array.isArray(files)) {
        files = [files];
      }
      for (let i = 0; i < files.length; i++) {
        formData.append(files[i].name, files[i].data, files[i].fileName);
      }
    }
    return formData;
  }

  static constructFormOrJsonData(params, files) {
    return files ? MonaiLabelClient.constructFormData(params, files) : params;
  }

  static api_get(url) {
    const Token = sessionStorage.getItem('Token')
    console.debug('GET:: ' + url);
    return axios
      .get(url, { headers: {"Authorization" : `${Token}`} })
      .then(function(response) {
        console.debug(response);
        return response;
      })
      .catch(function(error) {
        if(error.toString().includes('403')) window.location.pathname = '/ohif/login'
        
        return error;
      })
      .finally(function() {});
  }

  static api_delete(url) {
    const Token = sessionStorage.getItem('Token')
    console.debug('DELETE:: ' + url);
    return axios
      .delete(url, { headers: {"Authorization" : `${Token}`} })
      .then(function(response) {
        console.debug(response);
        return response;
      })
      .catch(function(error) {
        if(error.toString().includes('403')) window.location.pathname = '/ohif/login'
        
        return error;
      })
      .finally(function() {});
  }

  static api_post(
    url,
    params,
    files,
    form = true,
    responseType = 'arraybuffer'
  ) {
    const data = form
      ? MonaiLabelClient.constructFormData(params, files)
      : MonaiLabelClient.constructFormOrJsonData(params, files);
    return MonaiLabelClient.api_post_data(url, data, responseType);
  }

  static api_post_data(url, data, responseType) {
    const Token = sessionStorage.getItem('Token')
    console.debug('POST:: ' + url);
    return axios
      .post(url, data, {
        responseType: responseType,
        headers: {
          accept: ['application/json', 'multipart/form-data'],
          "Authorization" : `${Token}`
        },
      })
      .then(function(response) {
        console.debug(response);
        return response;
      })
      .catch(function(error) {
        if(error.toString().includes('403')) window.location.pathname = '/ohif/login'

        return error;
      })
      .finally(function() {});
  }

  static api_put(url, params, files, form = false, responseType = 'json') {
    const data = form
      ? MonaiLabelClient.constructFormData(params, files)
      : MonaiLabelClient.constructFormOrJsonData(params, files);
    return MonaiLabelClient.api_put_data(url, data, responseType);
  }

  static api_put_data(url, data, responseType = 'json') {
    const Token = sessionStorage.getItem('Token')
    console.debug('PUT:: ' + url);
    return axios
      .put(url, data, {
        responseType: responseType,
        headers: {
          accept: ['application/json', 'multipart/form-data'],
          "Authorization" : `${Token}`
        },
      })
      .then(function(response) {
        console.debug(response);
        return response;
      })
      .catch(function(error) {
        if(error.toString().includes('403')) window.location.pathname = '/ohif/login'

        return error;
      });
  }
}
