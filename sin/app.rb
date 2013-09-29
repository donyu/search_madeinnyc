require 'sinatra'
require 'sinatra/mongo'

set :mongo, 'mongo://localhost:27017/madenyc'

get '/' do
  mongo["startups"].find_one
end
