
import polars as pl

from sushi-train.data_io.local import (
	write_dataframe_to_local_csv,
	read_local_csv_to_dataframe,
	write_dataframe_to_local_parquet,
	read_local_parquet_to_dataframe,
	write_dataframe_to_local_json,
	read_local_json_to_dataframe,
)

def assert_frames_equal(left: pl.DataFrame, right: pl.DataFrame):
	assert left.to_dicts() == right.to_dicts()
	

def test_write_dataframe_to_local_csv(tmp_path):
	df = pl.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
	file_path = tmp_path / "test.csv"

	write_dataframe_to_local_csv(df, str(file_path))
	assert file_path.exists()
	assert file_path.stat().st_size > 0

	bad_path = tmp_path / "bad.csv"
	assert write_dataframe_to_local_csv(None, str(bad_path)) is None
	assert not bad_path.exists()


def test_read_local_csv_to_dataframe(tmp_path):
	df = pl.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
	file_path = tmp_path / "test.csv"
	df.write_csv(str(file_path))

	df2 = read_local_csv_to_dataframe(str(file_path))
	assert df2 is not None
	assert_frames_equal(df, df2)

	assert read_local_csv_to_dataframe(str(tmp_path / "no_such.csv")) is None


def test_write_dataframe_to_local_parquet(tmp_path):
	df = pl.DataFrame({"id": [10, 20], "flag": [True, False]})
	file_path = tmp_path / "test.parquet"

	write_dataframe_to_local_parquet(df, str(file_path))
	assert file_path.exists()
	assert file_path.stat().st_size > 0

	bad_path = tmp_path / "bad.parquet"
	assert write_dataframe_to_local_parquet(None, str(bad_path)) is None
	assert not bad_path.exists()


def test_read_local_parquet_to_dataframe(tmp_path):
	df = pl.DataFrame({"id": [10, 20], "flag": [True, False]})
	file_path = tmp_path / "test.parquet"
	df.write_parquet(str(file_path))

	df2 = read_local_parquet_to_dataframe(str(file_path))
	assert df2 is not None
	assert_frames_equal(df, df2)

	assert read_local_parquet_to_dataframe(str(tmp_path / "no_such.parquet")) is None


def test_write_dataframe_to_local_json(tmp_path):
	df = pl.DataFrame({"x": [0.1, 0.2], "y": ["u", "v"]})
	file_path = tmp_path / "test.json"

	write_dataframe_to_local_json(df, str(file_path))
	assert file_path.exists()
	assert file_path.stat().st_size > 0

	bad_path = tmp_path / "bad.json"
	assert write_dataframe_to_local_json(None, str(bad_path)) is None
	assert not bad_path.exists()


def test_read_local_json_to_dataframe(tmp_path):
	df = pl.DataFrame({"x": [0.1, 0.2], "y": ["u", "v"]})
	file_path = tmp_path / "test.json"
	df.write_json(str(file_path))

	df2 = read_local_json_to_dataframe(str(file_path))
	assert df2 is not None
	assert_frames_equal(df, df2)

	assert read_local_json_to_dataframe(str(tmp_path / "no_such.json")) is None
