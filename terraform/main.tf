terraform {
  backend "remote" {
    organization = "MichaelSenescall"

    workspaces {
      name = "bond-tutorial"
    }
  }
  required_providers = {
    heroku = {
      source  = "heroku/heroku"
      version = "4.6.0"
    }
  }
}

provider "heroku" {}