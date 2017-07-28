from requests import Session


def test_prepare_audit(auction, db):
    auction.prepare_audit()

    # {'auctionId': 'UA-11111',
    #  'auction_id': u'UA-11111',
    #  'id': u'UA-11111',
    #  'items': [{u'additionalClassifications': [{
    #                                                u'description': u'\u041f\u043e\u0441\u043b\u0443\u0433\u0438 \u0448\u043a\u0456\u043b\u044c\u043d\u0438\u0445 \u0457\u0434\u0430\u043b\u0435\u043d\u044c',
    #                                                u'id': u'55.51.10.300',
    #                                                u'scheme': u'\u0414\u041a\u041f\u041f'}],
    #             u'classification': {
    #                 u'description': u'\u041f\u043e\u0441\u043b\u0443\u0433\u0438 \u0437 \u0445\u0430\u0440\u0447\u0443\u0432\u0430\u043d\u043d\u044f \u0443 \u0448\u043a\u043e\u043b\u0430\u0445',
    #                 u'id': u'55523100-3',
    #                 u'scheme': u'CPV'},
    #             u'description': u'\u041f\u043e\u0441\u043b\u0443\u0433\u0438 \u0448\u043a\u0456\u043b\u044c\u043d\u0438\u0445 \u0457\u0434\u0430\u043b\u0435\u043d\u044c',
    #             u'quantity': 5,
    #             u'unit': {u'name': u'item'}}],
    #  'timeline': {'auction_start': {'initial_bids': []},
    #               'round_1': {},
    #               'round_2': {},
    #               'round_3': {}}}

    assert set(['id', 'auctionId', 'auction_id', 'timeline', 'items']) == set(auction.audit.keys())
    assert auction.audit['id'] == 'UA-11111'
    assert auction.audit['auctionId'] == 'UA-11111'
    assert auction.audit['auction_id'] == 'UA-11111'
    assert len(auction.audit['timeline']) == 4
    assert 'auction_start' in auction.audit['timeline']
    for i in range(1, len(auction.audit['timeline'])):
        assert 'round_{0}'.format(i) in auction.audit['timeline'].keys()
    auction.lot_id = '2222222222222222'
    auction.prepare_audit()

    assert auction.audit['lot_id'] == '2222222222222222'


def test_approve_audit_info_on_bid_stage(auction, db):
    auction.prepare_auction_document()
    auction.get_auction_info()
    auction.prepare_auction_stages_fast_forward()

    auction.current_stage = 7
    auction.current_round = auction.get_round_number(
        auction.auction_document["current_stage"]
    )
    auction.prepare_audit()
    auction.auction_document["stages"][auction.current_stage]['changed'] = True

    auction.approve_audit_info_on_bid_stage()

    # auction.audit == {'id': u'UA-11111',
    #                   'tenderId': u'UA-11111',
    #                   'tender_id': u'UA-11111',
    #                   'timeline': {'auction_start': {'initial_bids': []},
    #                                'round_1': {},
    #                                'round_2': {},
    #                                'round_3': {'turn_1': {'amount': 475000.0,
    #                                                       'bid_time': '2014-11-19T08:22:21.726234+00:00',
    #                                                       'bidder': u'd3ba84c66c9e4f34bfb33cc3c686f137',
    #                                                       'time': '2017-07-27T11:27:20.302787+03:00'}}}}

    assert 'turn_1' in auction.audit['timeline']['round_3']
    assert auction.audit['timeline']['round_3']['turn_1']['bidder'] == 'd3ba84c66c9e4f34bfb33cc3c686f137'
    assert auction.audit['timeline']['round_3']['turn_1']['amount'] == 475000.0


def test_approve_audit_info_on_bid_stage_features(features_auction, db):
    features_auction.prepare_auction_document()
    features_auction.get_auction_info()
    features_auction.prepare_auction_stages_fast_forward()

    features_auction.current_stage = 7
    features_auction.current_round = features_auction.get_round_number(
        features_auction.auction_document["current_stage"]
    )
    features_auction.prepare_audit()
    features_auction.auction_document["stages"][features_auction.current_stage]['changed'] = True

    for i in range(1, len(features_auction.audit['timeline'])):
        assert features_auction.audit['timeline']['round_{0}'.format(i)] == {}

    features_auction.approve_audit_info_on_bid_stage()

    # {'auction_start': {'initial_bids': []},
    #  'round_1': {},
    #  'round_2': {},
    #  'round_3': {'turn_1': {'amount': 480000.0,
    #                         'amount_features': '57420895248973824375/140737488355328',
    #                         'bid_time': '2014-11-19T08:22:24.038426+00:00',
    #                         'bidder': u'5675acc9232942e8940a034994ad883e',
    #                         'coeficient': '36028797018963968/30624477466119373',
    #                         'time': '2017-07-27T11:33:31.876689+03:00'}}}

    assert features_auction.audit['timeline']['round_3']['turn_1']['amount_features'] \
        == '57420895248973824375/140737488355328'
    assert features_auction.audit['timeline']['round_3']['turn_1']['coeficient'] \
        == '36028797018963968/30624477466119373'


def test_approve_audit_info_on_announcement(auction, db):
    auction.prepare_auction_document()
    auction.get_auction_info()
    auction.prepare_auction_stages_fast_forward()

    auction.prepare_audit()

    auction.approve_audit_info_on_announcement()

    # {'id': u'UA-11111',
    #  'tenderId': u'UA-11111',
    #  'tender_id': u'UA-11111',
    #  'timeline': {'auction_start': {'initial_bids': []},
    #               'results': {'bids': [{'amount': 475000.0,
    #                                     'bidder': u'd3ba84c66c9e4f34bfb33cc3c686f137',
    #                                     'time': '2014-11-19T08:22:21.726234+00:00'},
    #                                    {'amount': 480000.0,
    #                                     'bidder': u'5675acc9232942e8940a034994ad883e',
    #                                     'time': '2014-11-19T08:22:24.038426+00:00'}],
    #                           'time': '2017-07-27T11:36:44.539117+03:00'},
    #               'round_1': {},
    #               'round_2': {},
    #               'round_3': {}}}

    assert len(auction.audit['timeline']) == 5
    assert 'results' in auction.audit['timeline']
    for i in range(2, len(auction.audit['timeline'])):
        assert 'round_{0}'.format(i-1) in auction.audit['timeline'].keys()
    results = auction.audit['timeline']['results']
    assert len(results['bids']) == 2

    assert results['bids'][0]['amount'] == 475000.0
    assert results['bids'][0]['bidder'] == 'd3ba84c66c9e4f34bfb33cc3c686f137'

    assert results['bids'][1]['amount'] == 480000.0
    assert results['bids'][1]['bidder'] == '5675acc9232942e8940a034994ad883e'


def test_upload_audit_file_with_document_service(auction, db, logger, mocker):
    from requests import Session as RequestsSession
    auction.session_ds = RequestsSession()
    auction.prepare_auction_document()
    auction.get_auction_info()

    res = auction.upload_audit_file_with_document_service()
    assert res is None  # method does not return anything

    mock_session_request = mocker.patch.object(Session, 'request', autospec=True)

    mock_session_request.return_value.json.return_value = {
        'data': {
            'id': 'UA-11111'
        }
    }

    res = auction.upload_audit_file_with_document_service('UA-11111')
    assert res == 'UA-11111'

    log_strings = logger.log_capture_string.getvalue().split('\n')
    assert log_strings[3] == 'Audit log not approved.'


def test_upload_audit_file_without_document_service(auction, db, logger):
    auction.prepare_auction_document()
    auction.get_auction_info()

    res = auction.upload_audit_file_without_document_service()
    assert res is None  # method does not return anything
    log_strings = logger.log_capture_string.getvalue().split('\n')
    assert log_strings[3] == 'Audit log not approved.'
