# Charity Commission datasette

Public data [from the charity commision](http://data.charitycommission.gov.uk/) pubished as a [datasette](https://datasette.readthedocs.io/en/stable/) at https://cc-datasette.3sd.io.

## Do it yourself

1. Install the requirements (`pip3 install datasette` and `pip3 install datasette-vega).

2. Download the latest data with `./download 2019-02` (replace `2019-02` with the desired year and month).

3. Import the data into an sqlite database with `./import`

4. Your sqlite database is available at `data/out/cc-datasette.db`/

## Publishing to docker

Mostly for my own reference:
```
datasette package data/out/cc-datasette.db --install=datasette-vega --metadata=metadata.json # update the date in the metadata
docker tag 6004d6c7012c michaelmcandrew/cc-datasette # using the final image hash  output by datasette package
docker push michaelmcandrew/cc-datasette
```

## License

 Contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

