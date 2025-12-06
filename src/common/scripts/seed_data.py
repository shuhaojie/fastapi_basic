import asyncio
import random
from datetime import datetime, timedelta
from typing import List
import argparse
from sqlalchemy import delete
from sqlalchemy.future import select
from src.core.server.database import AsyncSessionLocal
from src.features.user.models import User
from src.features.project.models import Project, ProjectType, project_viewers
from src.features.doc.models import Doc, DocStatus
from faker import Faker
import uuid

FAKER_AVAILABLE = True


class ORMDataGenerator:
    def __init__(self, locale='zh_CN'):
        """初始化数据生成器"""
        self.fake = Faker(locale) if FAKER_AVAILABLE else None

        # 存储生成的实例
        self.users: List[User] = []
        self.projects: List[Project] = []
        self.docs: List[Doc] = []

        # 统计信息
        self.stats = {
            'users': 0,
            'projects': 0,
            'project_viewers': 0,
            'docs': 0
        }

    async def init_session(self):
        """初始化数据库会话"""
        self.db = AsyncSessionLocal()
        return self.db

    async def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'db') and self.db:
            await self.db.close()

    def _random_datetime(self, start_year: int = 2023, end_year: int = 2024) -> datetime:
        """生成随机日期时间"""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)

        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)

        # 添加随机时间
        random_hour = random.randint(0, 23)
        random_minute = random.randint(0, 59)
        random_second = random.randint(0, 59)

        return random_date.replace(hour=random_hour, minute=random_minute, second=random_second)

    def generate_users(self, count: int = 600) -> List[User]:
        """生成用户数据"""
        print(f"正在生成 {count} 个用户...")

        # 预定义一些常见中文姓氏和名字
        surnames = ['王', '李', '张', '刘', '陈', '杨', '赵', '黄', '周', '吴',
                    '徐', '孙', '胡', '朱', '高', '林', '何', '郭', '马', '罗']
        given_names = ['伟', '芳', '娜', '秀英', '敏', '静', '丽', '强', '磊', '军',
                       '洋', '勇', '艳', '杰', '娟', '涛', '明', '超', '秀兰', '霞',
                       '刚', '平', '建华', '桂英', '文', '兰', '红', '金凤', '健', '淑英']

        for i in range(count):
            # 生成中文姓名
            surname = random.choice(surnames)
            given_name = random.choice(given_names)
            chinese_name = surname + given_name

            # 生成用户名（拼音格式）
            username = self._generate_pinyin_username(chinese_name, i)

            # 生成邮箱
            domain = random.choice(['company.com', 'enterprise.cn', 'corp.net', 'test.org'])
            email = f"{username}@{domain}"

            # 生成昵称
            nickname = chinese_name if random.random() > 0.3 else self._generate_english_nickname()

            # 生成头像URL（可选）
            avatar = None
            if random.random() > 0.5:
                avatar = f"https://avatar.example.com/{username}.jpg"

            # 创建用户实例
            user = User(
                username=username,
                email=email,
                hashed_password=User.make_password(username),  # 密码与用户名相同
                nickname=nickname,
                avatar=avatar,
                is_superuser=(i < 10),  # 前10个用户是超级用户
                is_deleted=(i % 100 == 0),  # 每100个用户有一个被删除
                create_time=self._random_datetime(),
                update_time=self._random_datetime()
            )

            self.users.append(user)
            self.stats['users'] += 1

        print(f"已生成 {len(self.users)} 个用户实例")
        return self.users

    def _generate_pinyin_username(self, chinese_name: str, index: int) -> str:
        """生成拼音格式的用户名，确保唯一性"""
        pinyin_map = {
            '王': 'wang', '李': 'li', '张': 'zhang', '刘': 'liu', '陈': 'chen',
            '杨': 'yang', '赵': 'zhao', '黄': 'huang', '周': 'zhou', '吴': 'wu',
            '徐': 'xu', '孙': 'sun', '胡': 'hu', '朱': 'zhu', '高': 'gao',
            '林': 'lin', '何': 'he', '郭': 'guo', '马': 'ma', '罗': 'luo',
            '伟': 'wei', '芳': 'fang', '娜': 'na', '秀英': 'xiuying', '敏': 'min',
            '静': 'jing', '丽': 'li', '强': 'qiang', '磊': 'lei', '军': 'jun',
            '洋': 'yang', '勇': 'yong', '艳': 'yan', '杰': 'jie', '娟': 'juan',
            '涛': 'tao', '明': 'ming', '超': 'chao', '秀兰': 'xiulan', '霞': 'xia'
        }

        parts = []
        for char in chinese_name:
            if char in pinyin_map:
                parts.append(pinyin_map[char])
            else:
                parts.append(char.lower())

        # 使用索引和随机数字确保唯一性
        base_username = ''.join(parts)
        # 始终添加索引和随机数字以确保唯一性
        username = f"{base_username}{index}_{random.randint(1, 999)}"

        return username

    def _generate_english_nickname(self) -> str:
        """生成英文昵称"""
        nicknames = ['Alex', 'Chris', 'David', 'Emma', 'Frank', 'Grace',
                     'Henry', 'Ivy', 'Jack', 'Kate', 'Leo', 'Mona', 'Nick',
                     'Olivia', 'Paul', 'Queen', 'Ryan', 'Sara', 'Tom', 'Uma']
        return random.choice(nicknames)

    def generate_projects(self, count: int = 550) -> List[Project]:
        """生成项目数据"""
        print(f"\n正在生成 {count} 个项目...")

        if not self.users:
            self.generate_users()

        # 获取活跃用户作为项目所有者
        active_users = [u for u in self.users if not u.is_deleted]

        # 项目类型和行业
        industries = ['金融科技', '医疗健康', '教育培训', '电子商务', '智能制造',
                      '文化娱乐', '新能源', '人工智能', '物联网', '区块链',
                      '农业科技', '物流运输', '房地产', '旅游服务', '媒体广告']

        # 项目名称模板
        project_name_templates = [
            "{industry}{suffix}项目",
            "{industry}智能{suffix}系统",
            "{company}的{industry}平台",
            "{location}{industry}解决方案",
            "新一代{industry}{suffix}"
        ]

        company_names = ['东方', '华润', '中兴', '华为', '腾讯', '阿里', '百度',
                         '字节跳动', '京东', '美团', '滴滴', '拼多多', '小米']
        suffixes = ['开发', '实施', '优化', '升级', '整合', '创新', '数字化转型']
        locations = ['北京', '上海', '深圳', '广州', '杭州', '成都', '武汉', '西安']

        for i in range(count):
            # 随机选择项目所有者
            owner = random.choice(active_users) if active_users else self.users[0]

            # 生成项目名称
            industry = random.choice(industries)
            template = random.choice(project_name_templates)

            if '{company}' in template:
                project_name = template.format(
                    company=random.choice(company_names),
                    industry=industry,
                    suffix=random.choice(suffixes),
                    location=random.choice(locations)
                )
            elif '{location}' in template:
                project_name = template.format(
                    location=random.choice(locations),
                    industry=industry,
                    suffix=random.choice(suffixes)
                )
            else:
                project_name = template.format(
                    industry=industry,
                    suffix=random.choice(suffixes)
                )

            # 随机选择项目类型
            project_type = random.choice([ProjectType.PRIVATE, ProjectType.PUBLIC])

            # 创建项目实例
            project = Project(
                name=project_name,
                owner_id=owner.id if hasattr(owner, 'id') else None,
                project_type=project_type.value,
                is_deleted=(i % 50 == 0),  # 每50个项目有一个被删除
                create_time=self._random_datetime(),
                update_time=self._random_datetime()
            )

            self.projects.append(project)
            self.stats['projects'] += 1

        print(f"已生成 {len(self.projects)} 个项目实例")
        return self.projects

    async def assign_project_viewers(self, max_viewers_per_project: int = 10) -> None:
        """为项目分配查看者"""
        print(f"\n正在为项目分配查看者...")

        if not self.projects:
            self.generate_projects()

        # 获取数据库中已插入的活跃用户
        stmt = select(User).where(User.is_deleted == False)
        result = await self.db.execute(stmt)
        active_users = result.scalars().all()

        viewer_associations = 0
        associations_to_insert = []

        # 获取当前最大id值
        from sqlalchemy import func
        stmt = select(func.max(project_viewers.c.id))
        result = await self.db.execute(stmt)
        max_id = result.scalar() or 0

        for project in self.projects:
            # 跳过已删除的项目
            if project.is_deleted:
                continue

            # 排除项目所有者
            available_users = [u for u in active_users if u.id != project.owner_id]

            if not available_users:
                continue

            # 随机选择查看者数量
            num_viewers = random.randint(1, min(max_viewers_per_project, len(available_users)))
            selected_viewers = random.sample(available_users, num_viewers)

            # 创建关联记录
            for viewer in selected_viewers:
                # 每个查看关系有50%的概率被标记为删除
                is_deleted = random.random() > 0.5

                if not is_deleted:
                    # 创建关联记录，手动生成递增的id值
                    max_id += 1
                    associations_to_insert.append({
                        'id': max_id,
                        'project_id': project.id,
                        'user_id': viewer.id,
                        'is_deleted': False
                    })
                    viewer_associations += 1

        # 批量插入关联记录
        if associations_to_insert:
            try:
                from sqlalchemy import insert
                await self.db.execute(insert(project_viewers), associations_to_insert)
                await self.db.commit()
                print(f"已插入 {len(associations_to_insert)} 条项目查看者关联记录")
            except Exception as e:
                await self.db.rollback()
                print(f"插入项目查看者关联记录失败: {e}")
                raise

        self.stats['project_viewers'] = viewer_associations
        print(f"共创建 {viewer_associations} 条项目查看者关联")

    def generate_docs(self, count: int = 650) -> List[Doc]:
        """生成文档数据"""
        print(f"\n正在生成 {count} 个文档...")

        if not self.projects:
            self.generate_projects()

        # 文档类型
        doc_types = ['合同', '报告', '方案', '计划', '协议', '规范', '指南', '手册',
                     '纪要', '通知', '函件', '请示', '批复', '总结', '分析']

        doc_prefixes = ['项目', '技术', '商业', '财务', '市场', '产品', '设计', '测试',
                        '用户', '系统', '安全', '质量', '运营', '管理', '战略']

        for i in range(count):
            # 随机选择活跃项目
            active_projects = [p for p in self.projects if not p.is_deleted]
            if not active_projects:
                continue

            project = random.choice(active_projects)

            # 随机选择一个用户作为文档所有者
            # 在实际数据库中，应该从项目成员中选择
            if self.users:
                owner = random.choice([u for u in self.users if not u.is_deleted])
            else:
                # 如果没有用户，创建一个虚拟的owner_id
                owner = None

            # 生成文档名称
            doc_type = random.choice(doc_types)
            prefix = random.choice(doc_prefixes)

            # 简化项目名，避免太长
            short_project_name = project.name[:20] if len(project.name) > 20 else project.name

            file_name = f"{prefix}{doc_type}-{short_project_name}-V{random.randint(1, 5)}.{random.randint(0, 3)}"

            # 生成UUID
            file_uuid = str(uuid.uuid4())

            # 文档状态分布
            status_weights = [0.05, 0.1, 0.8, 0.05]  # 排队中5%，审核中10%，审核成功80%，审核失败5%
            status_value = random.choices([0, 1, 2, 3], weights=status_weights)[0]

            # 创建文档实例
            doc = Doc(
                file_name=file_name,
                file_uuid=file_uuid,
                owner_id=owner.id if owner else None,
                project_id=project.id if hasattr(project, 'id') else None,
                status=status_value,
                is_deleted=(i % 80 == 0),  # 每80个文档有一个被删除
                create_time=self._random_datetime(),
                update_time=self._random_datetime()
            )

            self.docs.append(doc)
            self.stats['docs'] += 1

        print(f"已生成 {len(self.docs)} 个文档实例")
        return self.docs

    async def insert_users_batch(self, batch_size: int = 100) -> None:
        """批量插入用户数据"""
        print(f"\n正在批量插入用户数据（每批 {batch_size} 条）...")

        if not self.users:
            self.generate_users()

        total_users = len(self.users)

        try:
            for i in range(0, total_users, batch_size):
                batch = self.users[i:i + batch_size]
                self.db.add_all(batch)
                await self.db.flush()  # 部分提交，获取ID
                await self.db.commit()  # 完全提交
                print(f"已插入用户 {i + 1} 到 {min(i + batch_size, total_users)}")

            # 重新查询以获取所有用户的ID
            stmt = select(User)
            result = await self.db.execute(stmt)
            self.users = result.scalars().all()

            print(f"用户数据插入完成，共 {total_users} 条记录")
        except Exception as e:
            await self.db.rollback()
            print(f"插入用户数据失败: {e}")
            raise

    async def insert_projects_batch(self, batch_size: int = 100) -> None:
        """批量插入项目数据"""
        print(f"\n正在批量插入项目数据（每批 {batch_size} 条）...")

        if not self.projects:
            self.generate_projects()

        # 确保用户ID已设置
        for project in self.projects:
            if project.owner_id is None and self.users:
                # 随机选择一个用户作为所有者
                owner = random.choice([u for u in self.users if not u.is_deleted])
                project.owner_id = owner.id

        total_projects = len(self.projects)

        try:
            for i in range(0, total_projects, batch_size):
                batch = self.projects[i:i + batch_size]
                self.db.add_all(batch)
                await self.db.flush()  # 部分提交，获取ID
                await self.db.commit()  # 完全提交
                print(f"已插入项目 {i + 1} 到 {min(i + batch_size, total_projects)}")

            # 重新查询以获取所有项目的ID
            stmt = select(Project)
            result = await self.db.execute(stmt)
            self.projects = result.scalars().all()

            print(f"项目数据插入完成，共 {total_projects} 条记录")
        except Exception as e:
            await self.db.rollback()
            print(f"插入项目数据失败: {e}")
            raise

    async def insert_docs_batch(self, batch_size: int = 100) -> None:
        """批量插入文档数据"""
        print(f"\n正在批量插入文档数据（每批 {batch_size} 条）...")

        if not self.docs:
            self.generate_docs()

        # 确保project_id和owner_id已设置
        for doc in self.docs:
            if doc.project_id is None and self.projects:
                # 随机选择一个项目
                project = random.choice([p for p in self.projects if not p.is_deleted])
                doc.project_id = project.id

            if doc.owner_id is None and self.users:
                # 随机选择一个用户
                owner = random.choice([u for u in self.users if not u.is_deleted])
                doc.owner_id = owner.id

        total_docs = len(self.docs)

        try:
            for i in range(0, total_docs, batch_size):
                batch = self.docs[i:i + batch_size]
                self.db.add_all(batch)
                await self.db.flush()
                await self.db.commit()
                print(f"已插入文档 {i + 1} 到 {min(i + batch_size, total_docs)}")

            print(f"文档数据插入完成，共 {total_docs} 条记录")
        except Exception as e:
            await self.db.rollback()
            print(f"插入文档数据失败: {e}")
            raise

    async def generate_all_data(self,
                                user_count: int = 600,
                                project_count: int = 550,
                                doc_count: int = 650,
                                insert_immediately: bool = True):
        """生成所有数据"""
        print("=" * 50)
        print("开始生成测试数据...")
        print("=" * 50)

        # 初始化会话
        await self.init_session()

        try:
            # 生成所有数据
            self.generate_users(user_count)
            self.generate_projects(project_count)
            self.generate_docs(doc_count)

            # 立即插入数据库
            if insert_immediately:
                await self.insert_users_batch()
                await self.insert_projects_batch()
                await self.assign_project_viewers()
                await self.insert_docs_batch()

            print("\n" + "=" * 50)
            print("数据生成完成！")

            return {
                'users': self.users,
                'projects': self.projects,
                'docs': self.docs
            }
        finally:
            await self.close()

    def print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 50)
        print("数据统计:")
        print(f"- 用户数量: {self.stats['users']}")
        print(f"- 项目数量: {self.stats['projects']}")
        print(f"- 项目查看者关联数量: {self.stats['project_viewers']}")
        print(f"- 文档数量: {self.stats['docs']}")

        print("\n示例数据:")

        if self.users:
            print(f"\n示例用户:")
            for i in range(min(3, len(self.users))):
                user = self.users[i]
                print(f"  {user.username} ({user.nickname}) - {user.email}")
                print(f"    密码: 与用户名相同，哈希值: {user.hashed_password[:20]}...")

        if self.projects:
            print(f"\n示例项目:")
            for i in range(min(3, len(self.projects))):
                project = self.projects[i]
                # 使用统计信息中的查看者数量，避免访问延迟加载的关系
                print(f"  {project.name}")
                print(f"    所有者ID: {project.owner_id}, 类型: {'公开' if project.project_type == 1 else '私有'}")
                print(f"    查看者数量: (统计值: {self.stats['project_viewers']})")

        if self.docs:
            print(f"\n示例文档:")
            for i in range(min(3, len(self.docs))):
                doc = self.docs[i]
                status_map = {0: '排队中', 1: '审核中', 2: '审核成功', 3: '审核失败'}
                print(f"  {doc.file_name}")
                print(f"    状态: {status_map.get(doc.status, '未知')}, UUID: {doc.file_uuid[:8]}...")

    async def cleanup(self):
        """清理测试数据（如果需要）"""
        print("\n正在清理测试数据...")

        try:
            # 初始化会话
            await self.init_session()

            # 注意：清理顺序与创建顺序相反（由于外键约束）
            await self.db.execute(delete(Doc))
            await self.db.execute(delete(project_viewers))
            await self.db.execute(delete(Project))
            await self.db.execute(delete(User))
            await self.db.commit()
            print("测试数据已清理")
        except Exception as e:
            await self.db.rollback()
            print(f"清理数据失败: {e}")
        finally:
            await self.close()


async def main_async(args):
    """异步主函数"""
    # 初始化数据生成器
    generator = ORMDataGenerator(locale='zh_CN')

    try:
        # 清理数据（如果需要）
        if args.cleanup:
            await generator.cleanup()
            return

        # 生成所有数据
        data = await generator.generate_all_data(
            user_count=args.users,
            project_count=args.projects,
            doc_count=args.docs,
            insert_immediately=not args.no_insert
        )

        # 打印统计信息
        generator.print_stats()

        print("\n" + "=" * 50)
        print("操作完成！")

    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成测试数据（ORM版本）')
    parser.add_argument('--users', type=int, default=600, help='用户数量')
    parser.add_argument('--projects', type=int, default=550, help='项目数量')
    parser.add_argument('--docs', type=int, default=650, help='文档数量')
    parser.add_argument('--no-insert', action='store_true', help='仅生成数据，不插入数据库')
    parser.add_argument('--cleanup', action='store_true', help='清理现有测试数据')
    parser.add_argument('--batch-size', type=int, default=100, help='批量插入大小')

    args = parser.parse_args()

    # 运行异步主函数
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()