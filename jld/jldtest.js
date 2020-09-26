const jsonld = require('jsonld');
const IdentifierIssuer = require('rdf-canonize').IdentifierIssuer;

var issuer = new IdentifierIssuer('xxx:yyy')

// Class declaration
class Cls {
  constructor(method1, method2) {
	this['@id'] = issuer.getId();
    this['xx:method1']= method1;
    this.method2= method2;
  }
}


var x = new Cls((xxx) => {console.log(xxx)})


console.log('js(on):');
console.log(x);


(async () => {
	const nquads = await jsonld.toRDF(x, {format: 'application/n-quads'});
	console.log('quads:');
	console.log(nquads)
})();
