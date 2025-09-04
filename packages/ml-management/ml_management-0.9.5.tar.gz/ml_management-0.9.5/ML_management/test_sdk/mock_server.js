// Mocking server by introspection.json
const { buildClientSchema } = require('graphql');

// create path to introspection.json
const path = require('path');
const introspectionPath = path.join(process.cwd(), '/introspection/output/introspection.json');
const introspectionResult = require(introspectionPath);

const { ApolloServer } = require('apollo-server');

console.log(introspectionResult);

const schema = buildClientSchema(introspectionResult);  

var json = {}
var json_str = "{}"

// mock some types
const mocks = {
    Long: () => 1000000,
    JSON: () => json,
    MethodSchema: () => ({
        schemaName: "predict_function",
    }),
    RoleMethodSchema: () => ({
        role: "single"
    })
  };

const server = new ApolloServer({
  schema,
  mocks: mocks,
});

server.listen().then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`)
});