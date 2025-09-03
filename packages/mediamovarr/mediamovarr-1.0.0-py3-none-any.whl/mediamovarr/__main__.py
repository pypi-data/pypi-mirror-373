"""Main CLI entry point for MediaMovarr."""

import logging
import sys
from pathlib import Path

import click

from .classify import MediaType, classify_media
from .confidence_rules import apply_confidence_rules
from .config import ConfigError, load_config
from .database import get_database
from .discovery import scan_for_media_folders
from .mover import MoveResult, move_media
from .renamer import get_renamed_path
from .tmdb_client import create_tmdb_client


def get_user_confirmation(
    folder_path: Path, media_type: str, confidence: float, dest_path: Path
) -> str:
    """
    Ask user for confirmation to move a media folder.

    Args:
        folder_path: Source folder path
        media_type: Detected media type
        confidence: Classification confidence score
        dest_path: Destination path

    Returns:
        User response: 'y' (yes), 'n' (no), 's' (skip all), 'e' (exclude)
    """
    print("\n🤔 CONFIRMATION NEEDED")
    print(f"   Folder: {folder_path.name}")
    print(f"   Detected as: {media_type} (confidence: {confidence:.1%})")
    print(f"   Would move to: {dest_path}")

    while True:
        response = (
            input("   Proceed? (y/n/s=skip all/e=exclude forever): ").lower().strip()
        )
        if response in ["y", "yes"]:
            return "y"
        elif response in ["n", "no"]:
            return "n"
        elif response in ["s", "skip"]:
            print("   Skipping all remaining confirmations...")
            return "s"
        elif response in ["e", "exclude"]:
            print("   Adding to exclusion list...")
            return "e"
        else:
            print(
                "   Please enter 'y' for yes, 'n' for no, 's' to skip all, or 'e' to exclude forever"
            )


def setup_logging(verbose: bool) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def run_prechecks(config_path: str, config_data: dict) -> bool:
    """
    Run pre-flight checks to validate configuration and environment.

    Args:
        config_path: Path to the configuration file
        config_data: Loaded configuration data

    Returns:
        True if all checks pass, False otherwise
    """
    logger = logging.getLogger(__name__)
    logger.info("Running pre-flight checks...")

    checks_passed = True

    # Check 1: Configuration file exists and is readable
    config_file = Path(config_path)
    if not config_file.exists():
        logger.error(f"❌ Configuration file not found: {config_path}")
        logger.error(
            "   Please create a config.json file or specify a different path with --config"
        )
        return False
    logger.info("✅ Configuration file exists")

    # Check 2: Required configuration fields
    required_fields = ["scan_dirs", "dest_dir"]
    for field in required_fields:
        if field not in config_data:
            logger.error(f"❌ Missing required configuration field: {field}")
            checks_passed = False
        else:
            logger.info(f"✅ Required field '{field}' is present")

    # Check 3: Scan directories exist and are readable
    scan_dirs = config_data.get("scan_dirs", [])
    if not scan_dirs:
        logger.error("❌ No scan directories configured")
        checks_passed = False
    else:
        for scan_dir in scan_dirs:
            scan_path = Path(scan_dir)
            if not scan_path.exists():
                logger.warning(f"⚠️  Scan directory does not exist: {scan_dir}")
            elif not scan_path.is_dir():
                logger.error(f"❌ Scan path is not a directory: {scan_dir}")
                checks_passed = False
            else:
                logger.info(f"✅ Scan directory accessible: {scan_dir}")

    # Check 4: Destination directory exists or can be created
    dest_dir = config_data.get("dest_dir")
    if dest_dir:
        dest_path = Path(dest_dir)
        if not dest_path.exists():
            try:
                dest_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created destination directory: {dest_dir}")
            except Exception as e:
                logger.error(f"❌ Cannot create destination directory: {e}")
                checks_passed = False
        elif not dest_path.is_dir():
            logger.error(f"❌ Destination path is not a directory: {dest_dir}")
            checks_passed = False
        else:
            logger.info(f"✅ Destination directory accessible: {dest_dir}")

    # Check 5: TMDb configuration if enabled
    if config_data.get("tmdb_enabled"):
        tmdb_api_key = config_data.get("tmdb_api_key") or config_data.get(
            "tmdb_read_access_token"
        )
        if not tmdb_api_key:
            logger.error(
                "❌ TMDb is enabled but no API key or read access token provided"
            )
            logger.error(
                "   Add 'tmdb_api_key' or 'tmdb_read_access_token' to your config"
            )
            checks_passed = False
        else:
            logger.info("✅ TMDb credentials configured")

    # Check 6: Database initialization
    try:
        from .database import get_database

        get_database()
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        checks_passed = False

    if checks_passed:
        logger.info("🎉 All pre-flight checks passed!")
    else:
        logger.error("❌ Some pre-flight checks failed. Please fix the issues above.")

    return checks_passed


@click.command()
@click.option("--config", "-c", default="config.json", help="Configuration file path")
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be done without making changes",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--force", "-f", is_flag=True, help="Force overwrite existing files")
@click.option(
    "--no-interactive",
    is_flag=True,
    help="Disable user confirmations (auto-skip medium confidence items)",
)
@click.option(
    "--skip-prechecks", is_flag=True, help="Skip pre-flight validation checks"
)
def main(
    config: str,
    dry_run: bool,
    verbose: bool,
    force: bool,
    no_interactive: bool,
    skip_prechecks: bool,
) -> None:
    """
    MediaMovarr - Organize downloaded media files according to Plex guidelines.

    Scans configured directories for media folders, classifies them by type
    (TV Show, Movie, Music, Audiobook), renames according to Plex standards,
    and moves them to organized destination folders.
    """
    setup_logging(verbose)
    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        logger.info(f"Loading configuration from {config}")
        config_data = load_config(config)

        # Run pre-flight checks
        if not skip_prechecks and not run_prechecks(config, config_data):
            logger.error("Pre-flight checks failed. Exiting.")
            sys.exit(1)

        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")

        # Scan for media folders
        logger.info("Scanning for media folders...")
        media_folders = list(scan_for_media_folders(config_data["scan_dirs"]))

        if not media_folders:
            logger.info("No media folders found in scan directories")
            return

        logger.info(f"Found {len(media_folders)} potential media folders")

        # Process each folder
        results = {"processed": 0, "moved": 0, "skipped": 0, "errors": 0}

        for folder_path in media_folders:
            try:
                results["processed"] += 1
                result = process_media_folder(
                    folder_path,
                    config_data,
                    dry_run=dry_run,
                    force=force,
                    interactive=not no_interactive,
                )

                if result == MoveResult.SUCCESS:
                    results["moved"] += 1
                elif result == MoveResult.SKIPPED:
                    results["skipped"] += 1
                else:
                    results["errors"] += 1

            except Exception as e:
                logger.error(f"Error processing {folder_path}: {e}")
                results["errors"] += 1

        # Print summary
        print("\n" + "=" * 60)
        print("PROCESSING SUMMARY")
        print("=" * 60)
        print(f"Folders processed: {results['processed']}")
        print(f"Successfully moved: {results['moved']}")
        print(f"Skipped: {results['skipped']}")
        print(f"Errors: {results['errors']}")

        if dry_run:
            print("\nNOTE: This was a dry run - no actual changes were made")

    except ConfigError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


def process_media_folder(
    folder_path: Path,
    config: dict,
    dry_run: bool = False,
    force: bool = False,
    interactive: bool = True,
) -> MoveResult:
    """
    Process a single media folder.

    Args:
        folder_path: Path to the media folder
        config: Configuration dictionary
        dry_run: If True, only show what would be done
        force: If True, overwrite existing files
        interactive: If True, ask for confirmation on medium confidence items

    Returns:
        MoveResult indicating the outcome
    """
    logger = logging.getLogger(__name__)

    # Initialize database for exclusions and caching
    db = get_database()

    # Check if folder is in exclusions list
    if db.is_excluded(str(folder_path)):
        logger.info(f"Skipping excluded folder: {folder_path.name}")
        return MoveResult.SKIPPED

    # Try TMDb lookup for enhanced classification
    tmdb_client = None
    if config.get("tmdb_enabled"):
        tmdb_client = create_tmdb_client(config)

    # Classify media type (with TMDb enhancement if available)
    media_type, base_confidence, tmdb_match = classify_media(folder_path, tmdb_client)

    logger.info(f"Processing: {folder_path.name}")
    logger.info(f"  Type: {media_type} (base confidence: {base_confidence:.2f})")

    if media_type == MediaType.UNKNOWN:
        logger.warning("  Skipping unknown media type")
        db.add_processing_record(
            str(folder_path),
            folder_path.name,
            "unknown",
            0.0,
            action="skipped",
            details={"reason": "unknown_media_type"},
        )
        return MoveResult.SKIPPED

    # Apply confidence rules
    confidence, applied_rules = apply_confidence_rules(
        folder_path, base_confidence, media_type, config, tmdb_match
    )

    if applied_rules:
        logger.info(f"  Applied rules: {', '.join(applied_rules)}")
        logger.info(f"  Final confidence: {confidence:.2f} (was {base_confidence:.2f})")
    else:
        logger.info(f"  Final confidence: {confidence:.2f} (no rules applied)")

    # Get confidence thresholds from config
    thresholds = config.get(
        "confidence_thresholds", {"auto_process": 0.9, "require_confirmation": 0.5}
    )

    auto_threshold = thresholds["auto_process"]
    confirm_threshold = thresholds["require_confirmation"]

    # Check confidence levels
    if confidence < confirm_threshold:
        logger.warning(
            f"  Confidence too low ({confidence:.2f} < {confirm_threshold:.2f}), skipping"
        )
        db.add_processing_record(
            str(folder_path),
            folder_path.name,
            media_type,
            confidence,
            action="skipped",
            details={"reason": "low_confidence"},
        )
        return MoveResult.SKIPPED

    # Get destination path
    dest_path = get_renamed_path(folder_path, media_type, config)

    if dest_path is None:
        logger.warning("  Could not determine destination path")
        db.add_processing_record(
            str(folder_path),
            folder_path.name,
            media_type,
            confidence,
            action="error",
            details={"reason": "no_destination_path"},
        )
        return MoveResult.ERROR

    logger.info(f"  Destination: {dest_path}")

    # Check if user confirmation is needed
    needs_confirmation = confirm_threshold <= confidence < auto_threshold

    if needs_confirmation and not dry_run:
        if interactive:
            user_response = get_user_confirmation(
                folder_path, media_type, confidence, dest_path
            )
            if user_response == "e":
                # Add to exclusions
                db.add_exclusion(
                    str(folder_path),
                    folder_path.name,
                    media_type,
                    confidence,
                    "User excluded during processing",
                )
                logger.info("  Added to exclusions list")
                return MoveResult.SKIPPED
            elif user_response == "s":
                # Skip all - could implement a global skip flag
                logger.info("  User chose to skip all")
                return MoveResult.SKIPPED
            elif user_response != "y":
                logger.info("  User declined to move folder")
                db.add_processing_record(
                    str(folder_path),
                    folder_path.name,
                    media_type,
                    confidence,
                    action="skipped",
                    details={"reason": "user_declined"},
                )
                return MoveResult.SKIPPED
        else:
            logger.info(
                f"  Medium confidence ({confidence:.2f}) - skipping in non-interactive mode"
            )
            db.add_processing_record(
                str(folder_path),
                folder_path.name,
                media_type,
                confidence,
                action="skipped",
                details={"reason": "non_interactive_medium_confidence"},
            )
            return MoveResult.SKIPPED

    if dry_run:
        status = "[DRY RUN]"
        if needs_confirmation:
            if interactive:
                status += " [WOULD REQUIRE CONFIRMATION]"
            else:
                status += " [WOULD SKIP - MEDIUM CONFIDENCE]"
        logger.info(f"  {status} Would move to: {dest_path}")
        return MoveResult.SUCCESS

    # Perform the move
    move_result = move_media(folder_path, dest_path, force=force)

    # Record the processing result in database
    if move_result == MoveResult.SUCCESS:
        db.add_processing_record(
            str(folder_path),
            folder_path.name,
            media_type,
            confidence,
            str(dest_path),
            "moved",
            {"tmdb_match": tmdb_match},
        )
        logger.info("  Move completed successfully")
    else:
        db.add_processing_record(
            str(folder_path),
            folder_path.name,
            media_type,
            confidence,
            action="error",
            details={"reason": "move_failed"},
        )
        logger.error("  Move failed")

    return move_result


if __name__ == "__main__":
    main()
