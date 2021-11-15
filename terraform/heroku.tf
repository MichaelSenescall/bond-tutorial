resource "heroku_app" "bond_tutorial_app" {
  name   = "bond-tutorial"
  stack  = "container"
  region = "us"
}

resource "heroku_build" "bond_tutorial_build" {
  app = heroku_app.bond_tutorial_app.id

  source {
    path = "../app"
  }
}