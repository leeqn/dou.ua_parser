import argparse
from sqlalchemy import create_engine,text
import asyncio
from templates.dou import DouParser

PARSER_REGISTRY={
    'dou':(DouParser,lambda req: f'https://jobs.dou.ua/vacancies/?search={req}')
}

async def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('-r','--request',default='Python',help="Enter your search query")
    parser.add_argument(
        '-s',
        '--sites',
        nargs='+',choices=list(PARSER_REGISTRY.keys())+['all'],
        default=['all'],
        help="Enter your sites")
    parser.add_argument(
        '--db',
        type=str,
        default='postgresql://user:password@localhost:5432/dbname',
        help="Enter your username")
    args = parser.parse_args()

    engine = create_engine(args.db, pool_pre_ping=True)
    with engine.begin() as conn:
        conn.execute(text('''CREATE TABLE IF NOT EXISTS vacancies
                             (id SERIAL PRIMARY KEY,
                                 title TEXT NOT NULL,
                                 company TEXT NOT NULL,
                                 link TEXT NOT NULL UNIQUE,
                                 raw_text TEXT,
                                 found_skills TEXT)'''))
    selected_sites=list(PARSER_REGISTRY.keys()) if "all" in args.sites else args.sites
    tasks=[]
    for site_key in selected_sites:
        parser_cls, url_builder = PARSER_REGISTRY[site_key]
        target_url = url_builder(args.request)
        parser_instance = parser_cls(engine)
        tasks.append(parser_instance.run(target_url))
        
    print(f"Run: {', '.join(selected_sites)}...")
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())