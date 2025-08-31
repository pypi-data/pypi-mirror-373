import polars as pl
import tldextract

from ascii_library.cleanup.commoncrawl.urls import get_surt_host


def perform_extract(x):
    if x is not None:
        extracted = tldextract.extract(x, include_psl_private_domains=True)
        registered_domain = extracted.registered_domain
        if registered_domain == "":
            registered_domain = f"{extracted.subdomain}.{extracted.domain}"
        return registered_domain
    else:
        return None


def clean_urls(combined_seeds: pl.DataFrame):
    """Input: Ploars dataframe with column: website_address"""
    return (
        combined_seeds.with_columns(
            pl.col("website_address")
            .str.to_lowercase()
            .str.replace("www..", "", literal=True)
            .str.replace("http:", "", literal=True)
            .str.replace("https:", "", literal=True)
            .str.replace("www.", "", literal=True)
            .str.replace("..", "", literal=True)
            .str.strip_chars("/")
            .str.split("/")
            .list.get(0)
            .str.replace("szmaxun.con", "szmaxun.com", literal=True)
            .alias("seed_node_url")
        )
        .with_columns(
            pl.col("seed_node_url")
            .map_elements(
                lambda x: (
                    tldextract.extract(
                        x, include_psl_private_domains=True
                    ).registered_domain
                    if x is not None
                    else None
                ),
                return_dtype=pl.String,
            )
            .alias("extracted")
        )
        .filter(
            (pl.col("seed_node_url").str.len_bytes() >= 4)
            & (pl.col("seed_node_url").is_not_null())
        )
        .with_columns(
            pl.col("extracted")
            .map_elements(
                lambda x: get_surt_host(perform_extract(f"https://{x}"))
                if x is not None
                else None,
                return_dtype=pl.String,
            )
            .alias("seed_node_url_surt")
        )
    )


def filter_sane_urls(combined_seeds: pl.DataFrame):
    """Input: Ploars dataframe of shape: ascii_id_company, website_address"""
    df = clean_urls(combined_seeds)

    # the following nodes would be deleted
    to_remove = df.filter(
        pl.col("extracted") != pl.col("seed_node_url"),
        ~pl.col("extracted").is_in(["1688.com"]),
        pl.col("extracted").str.len_bytes() < 4,
    ).to_pandas()
    if to_remove.shape[0] > 0:
        print(f"Removing the following weird URLs: {to_remove.shape}")
        print(to_remove)
        print(f"before removal: {df.shape}")

    df_seeds_duplicated = df.filter(
        ~pl.col("extracted").is_in(["1688.com"]),
        pl.col("extracted").str.len_bytes() >= 4,
        pl.col("extracted").is_not_null(),
    ).select(
        pl.col("ascii_id_company"),
        pl.col("extracted").alias("seed_node_url"),
        pl.col("seed_node_url_surt"),
    )
    print(f"df_seeds_duplicated: {df_seeds_duplicated.shape}")

    df_seeds_production = df_seeds_duplicated.unique(subset=["seed_node_url"])
    print(f"df_seeds_production: {df_seeds_production.shape}")
    return df_seeds_production, df_seeds_duplicated, to_remove


def upload_seeds_to_s3(
    fs,
    filename: str,
    df_seeds_production: pl.DataFrame,
    df_seeds_duplicated: pl.DataFrame,
    BUCKET_NAME: str = "ascii-supply-chain-research-input",
):
    with fs.open(
        f"{BUCKET_NAME}/ascii_seeds/seeds_deduplicated/seeds={filename}/seeds.parquet",
        mode="wb",
    ) as f:
        df_seeds_production.write_parquet(f, compression="gzip")
    with fs.open(
        f"{BUCKET_NAME}/ascii_seeds/seeds_not_deduplicated/seeds={filename}/seeds_duplicated.parquet",
        mode="wb",
    ) as f:
        df_seeds_duplicated.write_parquet(f, compression="gzip")
