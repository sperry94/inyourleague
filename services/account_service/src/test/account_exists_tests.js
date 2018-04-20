const chai = require('chai');
const chaiHttp = require('chai-http');
const proxyquire = require('proxyquire').noCallThru();
const sinon = require('sinon');

const verifyIdTokenStub = sinon.stub();

const queryMock = sinon.stub();

const account_svc = proxyquire('../account_service', {
  'google-auth-library': {
    OAuth2Client: function(clientId) {
      this.verifyIdToken = verifyIdTokenStub
    }
  },
  'pg': {
    Pool: function(poolParams) {
      this.connect = () => {};
      this.query = queryMock
    }
  }
});

const assert = chai.assert;
const expect = chai.expect;

process.env.NODE_ENV = 'test';

chai.use(chaiHttp);

describe('Account Exists Tests', () => {
  it('401, without OAuthToken', async () => {
    const exists_res = await chai.request(account_svc)
      .get('/exists')
      .send()

    expect(exists_res).to.not.be.null;
    expect(exists_res).to.have.status(401);
    expect(exists_res.text).to.equal('No auth token was provided.');
  });

  it('401, with invalid OAuthToken', async () => {

    verifyIdTokenStub.returns(Promise.resolve(null));

    const exists_res = await chai.request(account_svc)
      .get('/exists')
      .set('Cookie', 'OAuthToken=InvalidToken')
      .send()

    expect(exists_res).to.not.be.null;
    expect(exists_res).to.have.status(401);
    expect(exists_res.text).to.equal('Token could not be verified.');
  })

  it('404, with not exists', async () => {

    verifyIdTokenStub.returns(Promise.resolve({
      getPayload: () => {
        return { sub: 456 };
      }
    }));

    queryMock.returns(Promise.resolve({
      rows: [
        {
          exists: false
        }
      ]
    }));

    const exists_res = await chai.request(account_svc)
      .get('/exists')
      .set('Cookie', 'OAuthToken=ValidToken2')
      .send()

    expect(exists_res).to.not.be.null;
    expect(exists_res).to.have.status(404);
    expect(exists_res.text).to.equal('The account does not exist.');
  })

  it('200, with does exist', async () => {

    verifyIdTokenStub.returns(Promise.resolve({
      getPayload: () => {
        return { sub: 456 };
      }
    }));

    queryMock.returns(Promise.resolve({
      rows: [
        {
          exists: true
        }
      ]
    }));

    const exists_res = await chai.request(account_svc)
      .get('/exists')
      .set('Cookie', 'OAuthToken=ValidToken1')
      .send()

    expect(exists_res).to.not.be.null;
    expect(exists_res).to.have.status(200);
  })
})