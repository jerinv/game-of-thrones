import pytest

from screentime_chart import read_data, create_dataset


@pytest.fixture()
def df():
    df = read_data()
    return df


def test_df_episodes_exists(df):
    assert "episodes" in df.columns


def test_df_has_nulls(df):
    data = create_dataset(df)
    assert data.isnull().sum().sum() == 0
