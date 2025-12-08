#!/usr/bin/env python3
"""
Batch process product images through rembg endpoint.
Removes backgrounds and updates database with new R2 URLs.
"""
import psycopg2
import requests
import time
import sys

DB_URL = "postgresql://neondb_owner:npg_Y3uQc9xVXgze@ep-bitter-frog-ahv64lf5-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require"
API_URL = "https://ffmpeg-suite-production.up.railway.app/rembg"
API_KEY = "sk_live_0ZCdL2N_zJC7SgkeVYQykjGlPvjGUld8_sp8fB1Gdr0"


def main():
    print("Connecting to database...")
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()

    # Fetch all rows
    cur.execute("SELECT id, image_url, title FROM product_images ORDER BY id")
    rows = cur.fetchall()

    total = len(rows)
    success = 0
    failed = 0

    print(f"Processing {total} images...\n")

    for i, (id, image_url, title) in enumerate(rows, 1):
        # Truncate title for display
        display_title = title[:40] + "..." if len(title) > 40 else title
        print(f"[{i}/{total}] ID={id} {display_title}")

        try:
            resp = requests.post(
                API_URL,
                headers={
                    "X-API-Key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "image_url": image_url,
                    "response_format": "url",
                    "folder": "product_images"
                },
                timeout=120
            )

            if resp.status_code == 200:
                data = resp.json()
                new_url = data["download_url"]
                processing_time = data.get("processing_time", 0)

                # Update database
                cur.execute(
                    "UPDATE product_images SET image_url = %s WHERE id = %s",
                    (new_url, id)
                )
                conn.commit()

                success += 1
                print(f"  -> {new_url} ({processing_time:.1f}s)")
            else:
                failed += 1
                print(f"  -> FAILED: {resp.status_code} - {resp.text[:100]}")

        except requests.exceptions.Timeout:
            failed += 1
            print("  -> FAILED: Request timeout")
        except Exception as e:
            failed += 1
            print(f"  -> FAILED: {str(e)}")

        # Small delay to avoid overwhelming the server
        time.sleep(0.3)

    cur.close()
    conn.close()

    print(f"\n{'='*50}")
    print(f"DONE! Processed {total} images")
    print(f"  Success: {success}")
    print(f"  Failed:  {failed}")
    print(f"{'='*50}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
