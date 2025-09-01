/* API for client signing. Based on cryptopro cadesplugin_api */

const btc_crypto_pro_managers = {};

BTCCryptoProClientManager = function (id = 'main_sign_manager') {

    let self = this;

    btc_crypto_pro_managers[id] = this;

    this.cadesplagin_loaded = false;

    this.tray = new Tray(`#${id}`);

    this.ask_url = '';
    this.ask_for_signet_url = '';
    this.detached_sign = true;
    this.signed_data_post_delay = 1000;
    this.certificates_data = {};  // certificates data store

    this.current_cert_thumbprint = '';
    self.request_key = '';

    this.signal_for_load_certificates = '';
    this.select_selector = '.js-crypto_client_manager-certificate_select';
    this.error_container_selector = '.js-modal_error_container';
    this.formset_form_selector = '.js-sign_formset_form';
    this.certificate_form_selector = '.js-sign_certificate_form';
    this.start_sign_btn_selector = '.js-crypto_pro_start_sign';
    this.skip_sign_btn_selector = '.js-crypto_pro_skip_sign';
    this.element_disable_class = 'disabled';
    this.element_hide_class = 'hidden';
    this.form_elements_container_selector = '';

    this.ERROR_MESSAGES = {
        'CREATE_SIGN_FAIL': 'Не удалось подписать. Ошибка: ',
        'CERTIFICATES_NOT_FOUND': 'Сертификат не найден: ',
        'CERTIFICATE_LOAD_ERROR': 'Ошибка загрузки сертификата: ',
        'CERTIFICATE_NOT_CHOSEN': 'Не выбран сертификат',
        'SEND_TO_SERVER_ERROR': 'Ошибка отправки на сервер',
        'CERTIFICATE_HAS_EXPIRED': 'Истек срок действия сертификата'
    };

    this.MESSAGES = {
        'SIGNET_PENDING': 'Добавление печати для файлов'
    };

    const current_date = moment().format('YYYY-MM-DD HH:mm:ss');
    this.certificate_test_data = {
        'data-version': 'test version',
        'data-subject-name': 'test name',
        'data-issuer-name': 'test name',
        'data-serial-number': 'test serial number',
        'data-key-algorithm': 'test key algorithm',
        'data-valid-from-date': current_date,
        'data-valid-to-date': current_date,
    };

    this.CAPICOM_CERTIFICATE_FIND_EXTENDED_PROPERTY = 6;
    this.CAPICOM_CERTIFICATE_FIND_SHA1_HASH = 0;

    this.SIGN_BASE64_CONFIG = {
        'CADESCOM_CADES_BES': 1,
        'CADESCOM_BASE64_TO_BINARY': 1,
        'PROPSET_OPTIONS': 1,
        'CADESCOM_HASH_ALGORITHM_CP_GOST_3411': 100,
        'CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256': 101,
        'CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_512': 102,
    };
    this.SIGN_ALGORITHM = {
        'ALGORITHM_2012_256': '1.2.643.7.1.1.1.1',
        'ALGORITHM_2012_512': '1.2.643.7.1.1.1.2',
    };
    this.SIGN_XML_CONFIG = {
        'XmlDsigGost3410Url': 'urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102001-gostr3411',
        'XmlDsigGost3411Url': 'urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr3411',
        'XmlDsigGost3410_2012_256Url': 'urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-256',
        'XmlDsigGost3411_2012_256Url': 'urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-256',
        'XmlDsigGost3410_2012_512Url': 'urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34102012-gostr34112012-512',
        'XmlDsigGost3411_2012_512Url': 'urn:ietf:params:xml:ns:cpxmlsec:algorithms:gostr34112012-512',
    };

    this.QUEUE = [];
    this.SIGNET_QUEUE = [];
    this.QUEUE_INIT_HEADER = {'subject': 'init_queue'};
    this.QUEUE_RETRIEVE_DATA_HEADER = {'subject': 'retrieve_data'};

    this.START_SIGN_HEADER = [{name: 'serialize_for_sign', value: ''}];
    this.COMPLETE_SIGN_HEADER = [{name: 'sign_complete', value: ''}];

    /*
    QUEUE = {
        OBJECT_HASH: {
            'REQUEST_KEY': '',  unique value
            'DATA_TO_SIGN': '', serialized state
            'STAGE': '1'        stage for get the next chunk
            'STAGES_NUM': '1'   total count of stages
        },
        ...
    }
    */

    this.getCertificateBySHA_HASH = function (cert_name, data_to_sign) {
        return new Promise(function (resolve, reject) {
            cadesplugin.async_spawn(function* (args) {
                try {
                    let oStore = yield cadesplugin.CreateObjectAsync('CAdESCOM.Store');
                    yield oStore.Open();
                    const certificates = yield oStore.Certificates;
                    const oCertificates = yield certificates.Find(self.CAPICOM_CERTIFICATE_FIND_SHA1_HASH, cert_name);

                    const certificates_count = yield oCertificates.Count;
                    if (certificates_count === 0) {
                        throw (self.ERROR_MESSAGES.CERTIFICATES_NOT_FOUND + args[0]);
                    }
                    const oCertificate = yield oCertificates.Item(1);
                    args[2](oCertificate);

                    yield oStore.Close();
                } catch (e) {
                    let error_message = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                    args[3](error_message);
                    reject(error_message)
                }
            }, cert_name, data_to_sign, resolve, reject);
        });
    };

    this.loadExistCertificates = function (set_by_thumbprint = null) {
        /*
        Load user local certificates
        */

        cadesplugin.async_spawn(function* (args) {
            let oStore = yield cadesplugin.CreateObjectAsync('CAdESCOM.Store');
            yield oStore.Open();

            let certificates = yield oStore.Certificates;
            let certificates_count = yield certificates.Count;

            let current_certificate = undefined;
            for (let i = 1; i <= certificates_count; i++) {
                try {
                    current_certificate = yield certificates.Item(i);
                } catch (e) {
                    console.log(self.ERROR_MESSAGES.CERTIFICATE_LOAD_ERROR + cadesplugin.getLastError(e));
                    return;
                }

                let validToDate = moment(yield current_certificate.ValidToDate);
                if (validToDate.isBefore()) continue;

                const certificate_data = {};
                const certificate_public_key = yield current_certificate.PublicKey();
                const certificate_public_ley_algorithm = yield certificate_public_key.Algorithm;

                certificate_data['data-key-algorithm'] = yield certificate_public_ley_algorithm.FriendlyName;
                certificate_data['data-key-algorithm-oid'] = yield certificate_public_ley_algorithm.Value;
                certificate_data['data-issuer-name'] = yield current_certificate.IssuerName;
                certificate_data['data-subject-name'] = yield current_certificate.SubjectName;
                certificate_data['data-serial-number'] = yield current_certificate.SerialNumber;
                certificate_data['data-version'] = yield current_certificate.Version;
                certificate_data['data-thumbprint'] = yield current_certificate.Thumbprint;
                certificate_data['data-valid-from-date'] = yield current_certificate.ValidFromDate;
                certificate_data['data-valid-to-date'] = yield current_certificate.ValidToDate;
                self.certificates_data[certificate_data['data-thumbprint']] = certificate_data;

                const certificate_text = self.formatCertificateDisplayName(certificate_data);
                self.addOptionToSelect(
                    self.select_selector,
                    certificate_text,
                    certificate_data['data-thumbprint'],
                    set_by_thumbprint === certificate_data['data-thumbprint'],
                    certificate_data
                );
            }
        });
    };

    this.formatCertificateDisplayName = function (certificate_data) {
        const subject_name_CN = self.getTagValue(certificate_data['data-subject-name'], 'CN=');
        const subject_name_E = self.getTagValue(certificate_data['data-subject-name'], 'E=');
        const valid_to_date_formatted = moment(certificate_data['data-valid-to-date']).format('DD.MM.YYYY');
        const certificate_name = subject_name_CN + subject_name_E;

        return certificate_name + ', годен до: ' + valid_to_date_formatted;
    };

    this.getTagValue = function (source, name) {
        /*
        Function for retrieving tag content in certificate description
        */

        let info_string = '';
        if (source.indexOf(name) !== -1) {
            info_string = source.substring(source.indexOf(name) + name.length, 200);
            if (info_string.indexOf(',') > 0) {
                info_string = info_string.substring(1, info_string.indexOf(',') - 1);
            }
        }
        return info_string;
    };

    this.addOptionToSelect = function (select_selector,
                                       text,
                                       value,
                                       selected,
                                       attrs = {},
                                       default_selected = false) {
        const select_element = $(select_selector);
        const option = new Option(text, value, default_selected, selected);
        $(option).attr(attrs);
        select_element.append(option);
    };

    this.setCertificateDataToForm = function (data = null, test = false) {
        const certificate_data = data || self.certificates_data[self.current_cert_thumbprint];

        if (certificate_data !== undefined) {
            $('input[name=cert_version]').val(certificate_data['data-version']);
            $('input[name=cert_subject_name]').val(certificate_data['data-subject-name']);
            $('input[name=cert_key_algorithm]').val(certificate_data['data-key-algorithm']);
            $('input[name=cert_key_algorithm_oid]').val(certificate_data['data-key-algorithm-oid']);
            $('input[name=cert_serial_number]').val(certificate_data['data-serial-number']);
            $('input[name=cert_issuer_name]').val(certificate_data['data-issuer-name']);
            $('input[name=cert_valid_from_date]').val(certificate_data['data-valid-from-date']);
            $('input[name=cert_valid_to_date]').val(certificate_data['data-valid-to-date']);

            if (test) {
                $.each($(self.formset_form_selector), function () {
                    $(this).find('input').first().val('test sign');
                })
            }
        }
    };

    this.signBASE64 = function (certificate_object, data_to_sign, object_hash) {
        /*
        Create sign for data in BASE64 encoding
        */

        return new Promise(function (resolve, reject) {
            cadesplugin.async_spawn(function* (args) {
                try {
                    const oSigner = yield cadesplugin.CreateObjectAsync('CAdESCOM.CPSigner');
                    yield oSigner.propset_Certificate(certificate_object);

                    const oSignedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.CadesSignedData");
                    yield oSignedData.propset_ContentEncoding(self.SIGN_BASE64_CONFIG.CADESCOM_BASE64_TO_BINARY);
                    yield oSignedData.propset_Content(data_to_sign);
                    yield oSigner.propset_Options(self.SIGN_BASE64_CONFIG.PROPSET_OPTIONS);

                    let response = undefined;
                    try {
                        response = yield oSignedData.SignCades(
                            oSigner,
                            self.SIGN_BASE64_CONFIG.CADESCOM_CADES_BES,
                            self.detached_sign
                        );
                    } catch (e) {
                        response = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                        console.log("ERROR signBASE64 response", response);
                        self.displayTrayError(object_hash, response);
                        reject(response)
                    }
                    resolve(response);
                    return response;
                } catch (e) {
                    const error_message = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                    reject(error_message);
                    self.displayTrayError(object_hash, error_message);

                }
            }, certificate_object, data_to_sign, object_hash, resolve, reject);
        });
    };

    this.signXML = function (certificate_object, data_to_sign, object_hash) {
        /*
        Create sign for XML
        */

        return new Promise(function (resolve, reject) {
            cadesplugin.async_spawn(function* (args) {
                try {
                    const oSigner = yield cadesplugin.CreateObjectAsync('CAdESCOM.CPSigner');
                    yield oSigner.propset_Certificate(certificate_object);

                    const pubKey = yield certificate_object.PublicKey();
                    const algo = yield pubKey.Algorithm;
                    const algoOid = yield algo.Value;
                    let signMethod = '';
                    let digestMethod = '';
                    if (algoOid === self.SIGN_ALGORITHM.ALGORITHM_2012_256) {
                        signMethod = self.SIGN_XML_CONFIG.XmlDsigGost3410_2012_256Url;
                        digestMethod = self.SIGN_XML_CONFIG.XmlDsigGost3411_2012_256Url;
                    } else if (algoOid === self.SIGN_ALGORITHM.ALGORITHM_2012_512) {
                        signMethod = self.SIGN_XML_CONFIG.XmlDsigGost3410_2012_512Url;
                        digestMethod = self.SIGN_XML_CONFIG.XmlDsigGost3411_2012_512Url;
                    } else {
                        signMethod = self.SIGN_XML_CONFIG.XmlDsigGost3410Url;
                        digestMethod = self.SIGN_XML_CONFIG.XmlDsigGost3411Url;
                    }

                    const oSignedXML = yield cadesplugin.CreateObjectAsync('CAdESCOM.SignedXML');
                    yield oSignedXML.propset_Content(data_to_sign);
                    yield oSignedXML.propset_SignatureType(+self.detached_sign);
                    yield oSignedXML.propset_SignatureMethod(signMethod);
                    yield oSignedXML.propset_DigestMethod(digestMethod);

                    let response = undefined;
                    try {
                        response = yield oSignedXML.Sign(oSigner);
                    } catch (err) {
                        response = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(err);
                        self.displayTrayError(object_hash, response);
                    }
                    resolve(response);
                    return response;
                } catch (e) {
                    const error_message = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                    reject(error_message);
                }
            }, certificate_object, data_to_sign, object_hash, resolve, reject);
        });
    };

    this.signBASE64_RAW = function (certificate_object, hashed_data_to_sign, object_hash) {
        /*
        Create sign for hash of data in BASE64 encoding
        */
        return new Promise(function (resolve, reject) {
            cadesplugin.async_spawn(function* (args) {
                try {
                    const oRawSignature = yield window.cadesplugin.CreateObjectAsync('CAdESCOM.RawSignature')
                    let response = undefined;
                    try {
                        let sRawSignature = yield oRawSignature.SignHash(
                            hashed_data_to_sign,
                            certificate_object,
                        );
                        response = btoa(reverseString(hexToString(sRawSignature)));
                    } catch (e) {
                        response = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                        console.log("ERROR signBASE64_RAW response", response);
                        reject(response)
                    }
                    resolve(response);
                    return response;
                } catch (e) {
                    const error_message = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                    reject(error_message);
                }
            }, certificate_object, hashed_data_to_sign, object_hash, resolve, reject);
        });
    };

    this.signBASE64_HASH = function (certificate_object, hashed_data_to_sign, object_hash) {
        /*
        Create sign for hash of data in BASE64 encoding
        */

        return new Promise(function (resolve, reject) {
            cadesplugin.async_spawn(function* (args) {
                try {
                    const oSigner = yield cadesplugin.CreateObjectAsync('CAdESCOM.CPSigner');
                    yield oSigner.propset_Certificate(certificate_object);

                    const oSignedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.CadesSignedData");
                    yield oSignedData.propset_ContentEncoding(self.SIGN_BASE64_CONFIG.CADESCOM_BASE64_TO_BINARY);
                    yield oSigner.propset_Options(self.SIGN_BASE64_CONFIG.PROPSET_OPTIONS);

                    let response = undefined;
                    try {
                        response = yield oSignedData.SignHash(
                            hashed_data_to_sign,
                            oSigner,
                            self.SIGN_BASE64_CONFIG.CADESCOM_CADES_BES);
                    } catch (e) {
                        response = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                        console.log("ERROR signBASE64_HASH response", response);
                        reject(response)
                    }
                    resolve(response);
                    return response;
                } catch (e) {
                    const error_message = self.ERROR_MESSAGES.CREATE_SIGN_FAIL + cadesplugin.getLastError(e);
                    reject(error_message);
                }
            }, certificate_object, hashed_data_to_sign, object_hash, resolve, reject);
        });
    };

    this.showError = function (error_text) {
        const error_container = $(self.error_container_selector);
        error_container.html(error_text);
        error_container.removeClass(self.element_hide_class);
    };

    this.hideError = function () {
        const error_container = $(self.error_container_selector);
        error_container.html('');
        error_container.addClass(self.element_hide_class);
    };

    this.putSignToFieldForObjectByHash = function (object_hash, sign_string) {
        const object_hash_field = $(`input[value=${object_hash}]`);
        object_hash_field.closest(self.formset_form_selector).find('input').first().val(sign_string);
    };

    this.getMethodForObjectByHash = function (object_hash) {
        const object_hash_field = $(`input[value=${object_hash}]`);
        const method_field = object_hash_field.closest(self.formset_form_selector).find('input').last();
        return method_field.val();
    };

    this.displayTrayError = function (object_hash, error_message,) {
        self.tray.addInfoRow(object_hash, error_message);
        self.tray.addProgressBarItemBarColor(object_hash, 'red');
        self.tray.updateHeaderTitle('Ошибка!');
    };

    this.flushActiveQueue = function () {
        self.QUEUE = {};
        self.SIGNET_QUEUE = {};
        self.request_key = undefined;
    };

    this.getQueue = function (callback) {
        const post_data = {
            ...{'request_key': self.request_key},
            ...self.QUEUE_INIT_HEADER,
        };

        $.when(ajaxPostRequest(self.ask_url, post_data)).then(function (data) {
            self.QUEUE = data;
            callback();
        });
    };

    this.runSign = function (callback) {

        const certificate_thumbprint = $(self.select_selector).val();

        if (!certificate_thumbprint) {
            self.showError(self.ERROR_MESSAGES.CERTIFICATE_NOT_CHOSEN);
        } else {
            const certificate_promise = self.getCertificateBySHA_HASH(certificate_thumbprint);
            certificate_promise.then(function (certificate_object) {
                callback(certificate_object);
            }, function (reason) {
                self.showError(reason);
            });
        }
    };

    this.askServer = function (certificate_object) {
        return new Promise(function (main_promise_resolve, main_promise_reject) {
            cadesplugin.async_spawn(function* (args) {

                let oHashedData = yield cadesplugin.CreateObjectAsync("CAdESCOM.HashedData");
                const pubKey = yield certificate_object.PublicKey();
                const algo = yield pubKey.Algorithm;
                const algoOid = yield algo.Value;

                let algorithm = '';
                if (algoOid === self.SIGN_ALGORITHM.ALGORITHM_2012_256) {
                    algorithm = self.SIGN_BASE64_CONFIG.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_256;
                } else if (algoOid === self.SIGN_ALGORITHM.ALGORITHM_2012_512) {
                    algorithm = self.SIGN_BASE64_CONFIG.CADESCOM_HASH_ALGORITHM_CP_GOST_3411_2012_512;
                } else {
                    algorithm = self.SIGN_BASE64_CONFIG.CADESCOM_HASH_ALGORITHM_CP_GOST_3411;
                }

                yield oHashedData.propset_Algorithm(algorithm);
                yield oHashedData.propset_DataEncoding(self.SIGN_BASE64_CONFIG.CADESCOM_BASE64_TO_BINARY);

                const queue_last_step_index = self.QUEUE.length - 1;
                let data_store = {};
                let stage = 0;
                let errors = [];

                processQueue();

                async function processQueue() {
                    while (stage <= queue_last_step_index) {
                        const queue_data = self.QUEUE[stage];
                        const method = self.getMethodForObjectByHash(queue_data['object_hash']);

                        // save necessary info
                        data_store[queue_data['object_hash']] = '';
                        // set method for send to the server
                        queue_data['method'] = method;

                        const post_data = {
                            ...queue_data,
                            ...self.QUEUE_RETRIEVE_DATA_HEADER,
                            'algorithm': algoOid,
                        };

                        await getAjaxPromise(post_data, method, data_store);
                        stage++;

                        if (stage > queue_last_step_index) {
                            main_promise_resolve();
                        }
                    }
                }

                function getAjaxPromise(post_data, method, data_store) {
                    return new Promise(function (resolve, reject) {
                        $.when(ajaxPostRequest(self.ask_url, post_data)).then(function (data) {
                            let promise = undefined;
                            const object_hash = data['object_hash'];

                            self.tray.addOrUpdateProgressBarItem(
                                data['object_hash'],
                                data['name'],
                                Math.round((data['stage'] / data['stages_num']) * 100)
                            );

                            if (method === 'xml' || method === 'base64') {
                                data_store[data['object_hash']] += data['data_to_sign'];

                                if (data['stage'] === data['stages_num']) {
                                    if (method === 'xml') {
                                        promise = self.signXML(certificate_object, data_store[object_hash], object_hash);
                                    } else {
                                        promise = self.signBASE64(certificate_object, data_store[object_hash], object_hash);
                                    }
                                }
                            } else if (method === 'base64_hash' ||  method === 'base64_raw') {
                                if (data['need_hash']) {
                                    oHashedData.Hash(data['data_to_sign']);
                                } else {
                                    oHashedData.SetHashValue(data['data_to_sign']);
                                }
                                if (data['stage'] === data['stages_num']) {
                                    if (method === 'base64_hash') {
                                        promise = self.signBASE64_HASH(certificate_object, oHashedData, object_hash);
                                    } else {
                                        promise = self.signBASE64_RAW(certificate_object, oHashedData, object_hash);
                                    }
                                    // reset oHashedData
                                    oHashedData.Value;
                                }
                            }

                            if (promise !== undefined) {
                                promise.then(function (created_sign) {
                                    self.putSignToFieldForObjectByHash(object_hash, created_sign);
                                    resolve();
                                }, function (reason) {
                                    self.displayTrayError(object_hash, reason);
                                    self.showError(reason);
                                    reject(reason)
                                });
                            } else {
                                resolve();
                            }
                        });
                    });
                }
            });
        })
    };

    this.askServerCallback = function (url) {
        self.flushActiveQueue();

        self.tray.updateHeaderTitle('Отправка данных на сервер');
        setTimeout(function () {
            const post_data = [
                ...self.getForms(),
                ...self.COMPLETE_SIGN_HEADER
            ];

            $.when(ajaxPostRequest(url, post_data)).then(function (final_data) {
                self.tray.updateHeaderTitle('Успех');
                const redirect_url = final_data['redirect_url'];
                const calledObject = final_data['called_object'];
                if (calledObject) {
                    $(document).trigger('sign-manager:success', final_data);
                } else if (redirect_url) {
                    window.location.href = redirect_url;
                } else {
                    window.location.reload();
                }
            }).fail(function () {
                self.showError(self.ERROR_MESSAGES.SEND_TO_SERVER_ERROR);
                self.tray.updateHeaderTitle('При отправке произошла ошибка');
            })
        }, self.signed_data_post_delay);
    };

    this.addSignet = function () {
        return new Promise(function (main_promise_resolve, main_promise_reject) {
            const certificate_form_data = self.getCertificateForm(true);
            const queue_last_step_index = self.SIGNET_QUEUE.length - 1;
            let stage = 0;

            processSignetQueue();

            async function processSignetQueue() {
                while (stage <= queue_last_step_index) {
                    const queue_data = self.SIGNET_QUEUE[stage];
                    const post_data = {
                        ...queue_data,
                        ...certificate_form_data
                    };

                    await getAjaxPromise(post_data, stage);
                    stage++;

                    if (stage > queue_last_step_index) {
                        main_promise_resolve();
                    }
                }
            }

            function getAjaxPromise(post_data, stage) {
                return new Promise(function (resolve, reject) {
                    $.when(ajaxPostRequest(self.ask_for_signet_url, post_data)).then(function (data) {
                        if (data['result'] === 'success') {
                            self.tray.addOrUpdateProgressBarItem(
                                'signet',
                                self.MESSAGES.SIGNET_PENDING,
                                Math.round(((stage + 1) / self.SIGNET_QUEUE.length) * 100)
                            );
                            resolve();
                        }
                    }).fail(function () {
                        self.showError(self.ERROR_MESSAGES.SEND_TO_SERVER_ERROR);
                    });
                })
            }
        });
    };

    this.blockButtons = function (sign = true, skip = true) {
        if (sign) {
            $(self.start_sign_btn_selector).addClass(self.element_disable_class);
        }
        if (skip) {
            $(self.skip_sign_btn_selector).addClass(self.element_disable_class);
        }
    };

    this.unblockButtons = function (sign = true, skip = true) {
        if (sign) {
            $(self.start_sign_btn_selector).removeClass(self.element_disable_class);
        }
        if (skip) {
            $(self.skip_sign_btn_selector).removeClass(self.element_disable_class);
        }
    };

    this.fillCertificatesSelect = function () {
        const exist_options = $(self.select_selector).first().find('option');

        if (exist_options.length === 1) {
            self.loadExistCertificates();
        }
    };

    this.getForms = function (convert_to_dict = false) {
        let data = $(self.form_elements_container_selector).find('input, select, textarea').serializeArray();

        if (convert_to_dict) {
            data = convertDataArrayToDict(data);
        }

        return data
    };

    this.getCertificateForm = function (convert_to_dict = false) {
        let data = $(self.certificate_form_selector).find('input, select, textarea').serializeArray();

        if (convert_to_dict) {
            data = convertDataArrayToDict(data);
        }

        return data
    };

    this.initTray = function () {
        $.each(self.QUEUE, function (index, queue_data) {
            self.tray.addOrUpdateProgressBarItem(
                queue_data['object_hash'],
                queue_data['name'],
                0
            );
        });
    };

    this.initSignetTray = function () {
        self.tray.addOrUpdateProgressBarItem(
            'signet',
            self.MESSAGES.SIGNET_PENDING,
            0
        );
    };

    this.checkCertificateIsActive = function () {
        const certificate_data = self.certificates_data[self.current_cert_thumbprint];

        if (certificate_data === undefined) {
            self.hideError();
            Boolean(self.current_cert_thumbprint) ?
                self.unblockButtons() :
                self.blockButtons(true, false)
        } else if (moment(certificate_data['data-valid-to-date']) < moment(certificate_data['data-valid-from-date'])) {
            self.showError(self.ERROR_MESSAGES.CERTIFICATE_HAS_EXPIRED);
            self.blockButtons(true, false);
        } else {
            self.unblockButtons();
        }
    };

    this.initSignals = function () {

        $(document).on('click', self.skip_sign_btn_selector, function (event) {
            self.hideError();
            self.setCertificateDataToForm(self.certificate_test_data, true);
            self.blockButtons();

            const url = $(this).data('management-url') || $(this).data('url');
            const post_data = [
                ...self.getForms(),
                ...self.COMPLETE_SIGN_HEADER
            ];

            $.when(ajaxPostRequest(url, post_data)).then(function (final_data) {
                const redirect_url = final_data['redirect_url']
                if (redirect_url) {
                    window.location.href = redirect_url;
                } else {
                    window.location.reload();
                }
            }).fail(function () {
                self.showError(self.ERROR_MESSAGES.SEND_TO_SERVER_ERROR);
            });
            event.preventDefault();
        });

        // wait for cadesplagin load
        cadesplugin.then(function () {
            self.cadesplagin_loaded = true;
            self.tray.initSignals();

            $(document).on('change', self.select_selector, function (event) {
                self.current_cert_thumbprint = $(this).val();
                self.checkCertificateIsActive();
                event.preventDefault();
            });

            if (self.signal_for_load_certificates) {
                $(document).on(self.signal_for_load_certificates, function (event) {
                    self.fillCertificatesSelect();
                    event.preventDefault();
                });
            }
            $(document).on('click', self.start_sign_btn_selector, function (event) {
                self.hideError();
                const url = $(this).data('management-url') || $(this).data('url');

                self.tray.openTray();

                const initial_post_data = [
                    ...self.getForms(),
                    ...self.START_SIGN_HEADER
                ];

                $.when(ajaxPostRequest(url, initial_post_data)).then(function (data) {
                    self.request_key = data['request_key'];
                    self.QUEUE = data['queue'];
                    self.SIGNET_QUEUE = data['signet_queue'];

                    self.initTray();
                    self.setCertificateDataToForm();

                    if (self.SIGNET_QUEUE.length) {
                        self.initSignetTray();
                        self.tray.updateHeaderTitle('Добавление подписи в файл');
                        self.runSign(function (certificate_object) {
                            self.blockButtons();
                            self.addSignet().then(function (resolve, reject) {
                                self.tray.updateHeaderTitle('Подписание');
                                self.askServer(certificate_object).then(function (resolve) {
                                    self.askServerCallback(url);
                                }, function (reason) {
                                    self.showError(reason)
                                });
                            });
                        });
                    } else {
                        self.runSign(function (certificate_object) {
                            self.blockButtons();
                            self.tray.updateHeaderTitle('Подписание');
                            self.askServer(certificate_object).then(function (resolve) {
                                self.askServerCallback(url);
                            }, function (reason) {
                                self.showError(reason)
                            });
                        });
                    }
                });
                event.preventDefault();
            });
        });
    };

    function ajaxPostRequest(url, post_data) {
        post_data['csrfmiddlewaretoken'] = $('input[name=csrfmiddlewaretoken]').val();
        return $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            async: false,  // need for correct storing of data-chunks
            data: post_data
        });
    }

    function convertDataArrayToDict(base_data) {
        let data = {};
        $.each(base_data, function (index, content) {
            data[content['name']] = content['value']
        });
        return data;
    }

    function hexToString(hex) {
        let string = '';
        for (let b = 0; b < hex.length; b += 2) {
            string += String.fromCharCode(parseInt(hex.substr(b, 2), 16));
        }
        return string;
    }

    function reverseString(str) {
        let newStr = '';
        for (let i = str.length - 1; i >= 0; i--) {
            newStr += str.charAt(i);
        }
        return newStr;
    }
};
